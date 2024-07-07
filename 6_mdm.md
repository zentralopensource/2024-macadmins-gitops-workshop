# MDM

We are going to use the MDM module in Zentral to fix some of the compliance checks. We will start by creating some configuration profiles and distribute them. We will then have a look at some other resources.

## Distribute configuration profiles


### Create some profiles

We will use the mSCP project to generate some configuration profiles, but feel free to use your own profiles if you have some that you usually like to use.

So, open the terminal and navigate to the mSCP repository.

Then launch the following command:

**You might need to customize the following command!**

- Replace the `800-53r5_moderate.yaml` filename with the actual value


```
./scripts/generate_guidance.py -p build/baselines/800-53r5_moderate.yaml
```

This will generate mobileconfig files in the `build/800-53r5_moderate/mobileconfigs/unsigned` folder in the mSCP repository.

We will now include them in the Terraform configuration manually.

### Add the profiles to the Terraform config.

We will pick some of the configuration profiles, and add them to the Terraform repository.

For example, let's use `com.apple.security.firewall.mobileconfig` to configure the firewall.

Copy this file to the `mobileconfigs` subfolder in the Terraform repository.

We now need to create a new `zentral_mdm_artifact` resource, link it to the MDM blueprint to put it in scope, and add a `zentral_mdm_profile` connected to it to load the `mobileconfig`.

It looks like that:

```terraform
resource "zentral_mdm_artifact" "mscp-firewall" {
  name      = "mSCP - firewall"
  type      = "Profile"
  channel   = "Device"
  platforms = ["macOS"]
}

resource "zentral_mdm_profile" "mscp-firewall-1" {
  artifact_id = zentral_mdm_artifact.mscp-firewall.id
  source      = filebase64("${path.module}/mobileconfigs/com.apple.security.firewall.mobileconfig")
  macos       = true
  version     = 1
}
```

This can be added to the `mdm_artifacts.tf` file for example.

> [!TIP]
>`mscp-firewall` and `mscp-firewall-1` are Terraform resource names. They must not change. A change of a name will lead to resource being re-created. (A [`moved`](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring#moved-block-syntax) block can be used for refactoring the code). You need to pick a naming convention and stick to it! As you probably know:
>
> There are 2 hard problems in computer science: cache invalidation, **naming things**, and off-by-1 errors. – Phil Karlton?

In Zentral, we keep the different versions of an attrifact, we do not change an artifact in place. This way, we know exactly which configuration is on a given device. A version can be removed once it is not present on enrolled devices anymore.

Now that we have the artifact, we need to link it to a blueprint. In the `mdm_default_blueprint.tf` file, add the following resource:

```terraform
resource "zentral_mdm_blueprint_artifact" "mscp-firewall" {
  blueprint_id = zentral_mdm_blueprint.default.id
  artifact_id  = zentral_mdm_artifact.mscp-firewall.id
  macos        = true
}
```

Why is it a separate resource ? Because the same artifacts can be added to different blueprints. There are also [other attributes](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/mdm_blueprint_artifact) available like `excluded_tag_ids` to change the scope of the artifact for a given blueprint.

You an now make a PR and deploy this into Zentral.

> [!TIP]
> One the PR is merged, go to the _MDM > Artifacts_ section of Zentral and look for the new artifact.
>
> The MDM will not automatically push new artifacts to your whole fleet (it could be thousands of machines!). You can instead go to the _MDM > Devices_ section, and open the detail view of an enrolled device. You will be able to see the currently installed artifacts. There is also a green button above the list of commands. Click on it to _ping_ the device. After a few seconds, you should see the new artifacts reported as present on the device (reload the page if necessary.)
>
> You can now re-run the compliance checks (_Force full sync_ action in the inventory + Managed Software Center _Check Again_) and see if the firewall checks are now OK.

We have decided to keep the mobileconfig files in the repository in their original form. You can use your favorite tools to generate them. Terraform and the HCL configuration language and functions unlock really powerful possibilities.

> [!TIP]

> Open the [Santa configuration profile](https://github.com/zentralopensource/zentral-cloud-tf-starter-kit/blob/67f324a6cc712e0474ce8441ae6fcf3ad0cd97fa/mobileconfigs/santa.default-configuration.v1.mobileconfig#L28-L32) in your repo or on GitHub.
>
> Notice that we use `fqdn` and `secret` variables. The secrets are not included in the repository!
>
> Look now at [the Terraform resource](https://github.com/zentralopensource/zentral-cloud-tf-starter-kit/blob/67f324a6cc712e0474ce8441ae6fcf3ad0cd97fa/mdm_artifacts.tf#L112-L125) for the corresponding profile.
>
> Notice how we use the [`templatefile`](https://developer.hashicorp.com/terraform/language/functions/templatefile) function to load the file and to pass the variables.
>
> Find the origin of the secret.

That's it for the mobileconfigs in Zentral. Let's move on!

## Filevault

FileVault could be configured with configuration profiles, but since it is a strong requirement for all organizations, and since it requires some orchestration, especially with the Private Recovery Key escrow, we have decided to simplify the process and built the management around a specific resource.

We are going to use a [`zentral_mdm_filevault_config`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/mdm_filevault_config) resource.

So, let's add a new resource to the `mdm_default_blueprint.tf` file in our repository:

```terraform
# FileVault

resource "zentral_mdm_filevault_config" "default" {
  name                         = "Default"
  escrow_location_display_name = "PSUMAC24 GitOps Workshop"
  at_login_only                = true
  bypass_attempts              = 0
  destroy_key_on_standby       = true
  show_recovery_key            = false
}
```

We also need to add this to the blueprint. We need to add a [`filevault_config_id`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/mdm_blueprint#filevault_config_id) attribute to the existing blueprint resource to point to the new config:

```terraform
resource "zentral_mdm_blueprint" "default" {
  name                 = "Default"
  collect_apps         = "ALL"
  collect_certificates = "ALL"
  collect_profiles     = "ALL"
  filevault_config_id  = zentral_mdm_filevault_config.default.id
}
```

As usual, commit your changes, make a Pull Request, review the changes and merge the PR to deploy the new configuration in your instance!

> [!TIP]
> In the _MDM > Blueprints_ section, open the blueprint, and notice that it contains the new FileVault configuration.
>
> In the _MDM > Devices_ section, find your test device, and _ping_ it with the green button above the list of commands. Reload the page until you see that the FileVault setup was done.
>
> On your test device, logout and login again. It should trigger the FileVault setup.
>
> You can now re-run the compliance checks (_Force full sync_ action in the inventory + Managed Software Center _Check Again_) and see if the _FileVault enabled_ check is now OK.


## Software updates

Let's configure the software updates now. Software update enforcement was introduced one year ago with macOS 14. (Last month Apple announced a new declaration to manage even more settings, but we are still working on integrating this to Zentral!).

Let's add a [`zentral_mdm_software_update_enforcement`](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/mdm_software_update_enforcement) resource in the `mdm_default_blueprint.tf` file:

```terraform
# Software update enforcement

resource "zentral_mdm_software_update_enforcement" "default" {
  name           = "Default"
  platforms      = ["macOS"]
  max_os_version = "15"
  delay_days     = 7
}

```

Like the FileVault resource, we need to link this to the blueprint. But **UNLIKE** the FileVault resource, you can link multiple software update enforcement resources to the same blueprint. You can have different targets and delays, and scope the software update enforcement with [machine tags](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/mdm_software_update_enforcement#tag_ids).

Your blueprint resource should look like that:

```terraform
resource "zentral_mdm_blueprint" "default" {
  name                            = "Default"
  collect_apps                    = "ALL"
  collect_certificates            = "ALL"
  collect_profiles                = "ALL"
  filevault_config_id             = zentral_mdm_filevault_config.default.id
  recovery_password_config_id     = zentral_mdm_recovery_password_config.default.id
  software_update_enforcement_ids = [zentral_mdm_software_update_enforcement.default.id]
}
```

Again, commit your changes, make a Pull Request, review the changes and merge the PR to deploy the new configuration in your instance!

> [!TIP]
> In the _MDM > Blueprints_ section, open the blueprint, and notice that it contains the new FileVault configuration.
>
> In the _MDM > Devices_ section, find your test device, and _ping_ it with the green button above the list of commands. Reload the page until you see that a new `DeclarativeManagement` command was acknowledged.
>
> On the device, open the MDM profile and look for the new Software Update declaration.

## Enterprise apps

We have already configured an Enterprise App in your instance: the bootstrap package. Let's have a look at how we configured it, and which strategy we used to be able to load the package file.

> [!TIP]
> In the `mdm_artifacts.tf` file, find the [`Enterprise App`](https://github.com/zentralopensource/zentral-cloud-tf-starter-kit/blob/67f324a6cc712e0474ce8441ae6fcf3ad0cd97fa/mdm_artifacts.tf#L27-L35) artifact resource.
>
> Find the [resource](https://github.com/zentralopensource/zentral-cloud-tf-starter-kit/blob/67f324a6cc712e0474ce8441ae6fcf3ad0cd97fa/mdm_artifacts.tf#L37-L43) used to load the package.
>
> Notice that the file is not included in the repository, but loaded from AWS S3.
>
> Find the artifact in the _MDM > Artifacts_ section in Zentral.

This is it for the Zentral MDM configuration. Let's have a look at [Munki now](./7_munki.md).

