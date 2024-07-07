# Osquery

## Why Osquery?

[Osquery](https://osquery.io/) is an agent that present device resources as SQL tables. Queries can be schedule to run at regular interval or can be distributed ad-hoc. Logging modules ship the result of the queries back to a logging server.

We use Osquery in Zentral for visibility it gives us on the endpoints. Queries are automatically scheduled to gather hardware and software inventory information. The knownledge you might already have about Osquery is directly applicable. In Zentral, you will find Configurations, Packs, Queries, Distributed queries, Automatic Table constructions, …

The instances we prepare for Zentral Cloud come with a default Osquery configuration where the inventory collection is turned on. Let's add our first query pack and query to it.

## Add a query

We are going to add a query, and schedule it by adding it to a pack that we will connect to the existing configuration.

First we add a [`zentral_osquery_pack`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/osquery_pack) resource to a new `osquery_compliance_checks.tf` file:

```terraform
resource "zentral_osquery_pack" "compliance-checks" {
  name        = "Compliance checks"
  description = "The compliance checks for our macOS client"
}
```

We then add a [`zentral_osquery_query`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/osquery_query) resource and schedule it within the pack:

```terraform
resource "zentral_osquery_query" "santa-sysext-cc" {
  name        = "Santa system extension check"
  description = "Check if the Santa system extension is activated, running and up-to-date"
  sql = trimspace(<<-EOT
  WITH expected_sysexts(team, identifier, min_version) AS (
    VALUES ('EQHXZ8M8AV', 'com.google.santa.daemon', '2024.5')
  ), found_sysexts AS (
    SELECT expected_sysexts.*, system_extensions.version, system_extensions.state,
    CASE
      WHEN system_extensions.version >= expected_sysexts.min_version
        AND system_extensions.state == 'activated_enabled'
      THEN 'OK'
      ELSE 'FAILED'
    END individual_ztl_status
    FROM expected_sysexts
    LEFT JOIN system_extensions ON (
      system_extensions.team = expected_sysexts.team
      AND system_extensions.identifier = expected_sysexts.identifier
    )
  ) SELECT team, identifier, version, state, MAX(individual_ztl_status) OVER () ztl_status
  FROM found_sysexts
  EOT
  )
  platforms                = ["darwin"]
  compliance_check_enabled = true
  scheduling = {
    pack_id             = zentral_osquery_pack.compliance-checks.id,
    interval            = var.osquery_default_compliance_check_interval,
    log_removed_actions = false,
    snapshot_mode       = true
  }
}
```

This query might seem complicated, but it is a pattern that is really useful, especially for compliance checks. The same way Munki script checks are compliance checks for Zentral, osquery queries can also be compliance checks if they return a `ztl_status` column with `OK` or `FAILED` values.

In the query, we are first describing the expected results. In that case, we want the Santa system extension version 2024.5 activated and enabled. We then do a _left join_ with the actual system extension, and calculate the result of the check. It is a bit more complicated in this case because older extensions might still be present, and we do not want the check to fail if the newer extension is OK.

In the `scheduling` block, we connect this query to a pack. For compliance checks queries, we only want the `snapshot_mode`, meaning that we want all the results of the query everytime osquery runs it. Osquery can run in diff mode, meaning that only added or removed results between two runs are sent to the log server.

We have also introduced a [variable](https://developer.hashicorp.com/terraform/language/values/variables): `osquery_default_compliance_check_interval`. This is one great advantage of the Terraform language. Instead of having hard coded values, you can rely on variables to be applied in all your resources. **But for this to work we need to define the variable!**

In the `variables.tf` file of the repo, we need to add this:

```terraform
variable "osquery_default_compliance_check_interval" {
  description = "Default Osquery compliance check scheduling interval in seconds"
  default     = 3600
}
```

Finally to distribute this pack, we need to attach it to the configuration. In the `osquery_configurations.tf` file, we need to add a [`zentral_osquery_configuration_pack`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/osquery_configuration_pack) resource:

```terraform
# Pack

resource "zentral_osquery_configuration_pack" "default-compliance-checks" {
  configuration_id = zentral_osquery_configuration.default.id
  pack_id          = zentral_osquery_pack.compliance-checks.id
}
```

> [!TIP]
> The name of the `.tf` files are only suggestions. Terraform will concatenate all the resources before building a dependency graph to apply them. It doesn't matter in which files the resources are.

Et voilà! Our compliance check is scheduled to run every hour. Commit your changes, make a Pull Request, review the changes and merge the PR to deploy the query in your instance!

> [!TIP]
> In the _Osquery > Queries_ view in Zentral, find your query.
>
> You can follow the link to the pack, and from the pack view, the link to the configuration.
>
> This compliance check is scheduled to run every hour, but we can speed things up by queueing a query run.
>
> From the Query view, at the bottom, click on the _Launch_ button. Save the form with the default values. It will offer the query to all the devices for 1 day by default. Devices are configured to connect to the server every two minutes to pick up ad-hoc queries to run ([distributed queries](https://osquery.readthedocs.io/en/stable/deployment/remote/#distributed-queries)).
>
> Reload the run view until you see some results coming from your test devices or VMs. You can then click on the _Results_ link.
>
> Go to the machine view in the inventory and look for the `Santa system extension check` compliance check. It should be set to `OK` (We know, we have to improve this UI a lot!!!).
>

For those of you familiar with Osquery, you might wonder while we have decided to write our packs with the Terraform language instead of just importing them like the MDM mobileconfig files.

Our packs and our queries have some extra functionalities that are not present in the Osquery pack format. The link between a pack and a query can be scoped with Tags for example to make the configuration more dynamic. Queries can also be used to set tags on the devices, when they return a result.

We also like the expressivity of the Terraform language more than the **slightly broken** default Osquery JSON… If you have packs and want to migrate them, there is an [API endpoint in Zentral](https://docs.zentral.io/en/latest/apps/osquery/#apiosquerypacksslugslug) to import standard Osquery packs. You can then use the Terraform export functionality in Zentral to get them in HCL/Terraform language.

That's it for Osquery. Let's now have a look at the last module we will cover today: [Google Santa](./9_santa.md).
