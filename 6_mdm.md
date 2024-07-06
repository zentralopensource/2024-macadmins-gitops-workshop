# MDM

We are going to use the MDM module in Zentral to fix some of the compliance checks. We will start by creating some configuration profiles and distribute them. We will then have a look at some other resources.

## Distribute some configuration profiles


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
 
