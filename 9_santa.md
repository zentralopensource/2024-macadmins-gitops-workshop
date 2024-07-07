# Google Santa

## What is Google Santa

[Google Santa](https://santa.dev) is a binary and file access authorization system for macOS.

Rules can be written to allow a block binaries. Google Santa can be configured to run in two different modes:

* `Monitor` mode which will allow binaries not covered by a rule to run, only blocking binaries covered by a blocking rule
* `Lockdown` mode which will block unknown binaries by default, only allowing those covered by a rule allowing them to run.

A standard implementation will start with Santa in `Monitor` mode to collect information about the software in your fleet. Rules will be added to cover the required software and block the unwanted software. Once the volume of unknown binaries has been reduced, the `Lockdown` mode can be activated on a subset of the fleet.

Rules can be written directly in a configuration file, but it is much more convenient to use a [sync server](https://santa.dev/deployment/sync-servers.html) to distribute the rules, and collect the events. This is where Zentral comes into play.

In your instance, Santa is already preconfigured and the agent has been deployed to your test devices or VMs.

> [!TIP]
> In Zentral, open the _Santa > Overview_ view.
>
> You should see some events in the bar graphs at the top.
>
> You should also see that there is one _Default_ configuration.
>
> If you click on the configuration, you should see that is it in `Monitor` mode, and that no rules are attached to it.
>
> Going back to the _Overview_ you may already have some _Collected targets_. Those are hashes, Team IDs, or Signing IDs extracted from the Santa events. Targets are binary identifiers used in the rules.
>
> Go to one of your machines view in the inventory, and click on the _Events_ button. Filter them by _Event type = Santa event_. You should see the events posted by the Santa agents from which we extract the targets.
>
> Each instance of Zentral in Zentral Cloud is configured with Grafana. In your instance, click on the screen button in the top right corner and select _Grafana_.
>
> In Grafana, go to the _Santa unknown targets_ dashboard. You will see aggregations of unknown Team IDs and Signing IDs extracted from the events.

Now that you are more familiar with Santa in Zentral, let's have a look at it from one of your test device or VM.

> [!TIP]
> Open a terminal, and run the `santactl status` command. Look at the output. You should see the mode, the sync server, and also that there are currently no rules.
>
> run the `santactl fileinfo /Applications/1Password.app` command. It will give you information about the binary, its signature, and the identifiers that we can use to target it.

Let's now write a rule to block a binary, and deploy it.

## Add a rule

Let's add a [`zentral_santa_rule`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/santa_rule) rule to the `santa_configurations.tf` file:

```terraform
resource "zentral_santa_rule" "teamid-macpaw" {
  configuration_id  = zentral_santa_configuration.default.id
  policy            = "BLOCKLIST"
  target_type       = "TEAMID"
  target_identifier = "S8EX82NJP6"
  custom_message    = "No MacPaw apps are allowed!!!"
  description       = "Block MacPaw apps, mostly for demo purposes"
}
```

With this example, we are blocking all the apps signed by MacPaw based on the Team ID. Feel free to use `santactl fileinfo` to target a different publisher, or be more granular with a Signing ID.

Commit your change, make a Pull Request, review the changes and merge the PR to deploy the new rule in your instance!

> [!TIP]
> Go to the _Santa > Configurations > Default_ view.
>
> You should now see that it contains 1 rule.
>
> Rules are synced by default every 10 minutes. We can speed things up. Run the `santactl sync` command on the test devices or VMs. You will see in the output that the new rule has been received.
>
> Launch the targeted binary, and a Santa popup will be displayed instead.
>
> In Zentral, find the execution event attached to the device. It should have a `BLOCK_TEAMID` decision.

That's it!!!

