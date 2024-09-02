# Introduction to GitOps

As [GitLab](https://about.gitlab.com/topics/gitops/) defines it, GitOps is:

> GitOps is an operational framework that takes DevOps best practices used for application development such as version control, collaboration, compliance, and CI/CD, and applies them to infrastructure automation.

The same proven principles can be applied to device managemenent. We will use a GitOps workflow to automate the process of configuring devices. We will use configuration files stored as code, in a version control system, and deploy the configuration with CI/CD pipelines.

_If you would like to learn or freshen up your skills with Git, you can use this [tutorial on branching with git](https://learngitbranching.js.org/)._  

### What are the benefits?

There are many, but let's start with:

 - Better auditability

    All changes are kept in the version control system. All the reviews can happen in a platform already in place in your organization (GitHub, GitLab, …)
    
 - Better reliability
    
    Errors can be caught before they are deployed in code reviews

 - Better collaboration

    Have junior CPEs propose changes in pull requests, and senior CPEs do code reviews, and approve the changes for deployment.
    
 - Better code re-use

    Since the configuration is written as code, it can be easily shared and re-used between users of the same product. Modules can be developped to abstract some of the boiler plate code.
    

## Where do we start?

### Write code, and find a tool to apply it.

First, we need to find a way to express the configuration of the devices as code. Then we need a mechanism to deploy this configuration.

This could be achieved many ways. For the configuration profiles, you could for example have them as files in a repo, and build a script to upload them to your MDM. This script can then be called from a CI/CD pipeline when a new version of the repository is merged.

But what about other pieces of configuration that cannot be expressed directly as code ? What about a new version of a package, or new application that needs to be blocked ? You would have to come up with your own language to define those resources, and you would have to update your script to manage these new resources. The script itself always has to do the same state management. Does the resource exist ? Is it in the same state ?, …

This could be manageable for a few resource types, but it gets complicated quickly.

### The origin of GitOps with Zentral

With Zentral, we started with indempotent APIs to be able to push Santa rules and have them synced to the server. But we quickly realized that maintaining special APIs for each resource would be a lot of work. 

The tools to apply the changes would be very specific to our platform too, reducing the possibilities for knowledge transfer.

So we looked at the systems already widly in used for IaC. In our organization we use Terraform a lot for our own infrastructure, and to deploy Zentral on prem for some of our customers. That gave us an idea: What if we could use Terraform to manage the Zentral configuration?

### Why Terraform (or OpenTofu)?

* A well established technology

    Terraform has become one of the reference tool for IaC. A lot of integrations are available (Terraform Cloud with GitHub, GitLab pipelines with Terraform state support, …). A lot of resources are available online to help the users. People already familiar with it could use the same skills and workflows for maintaining Zentral.
    
* A good (enough) language (HCL)

    Remember that for GitOps, you have to maintain your configuration as code. Terraform comes with HCL, a powerful language to descript resources. It has a lot of integrated tools to read files from disk, or resources from URLs, to loop on data sources, …
    
* It manages the state for us!

    The common loop "Does it exist? Update or Create or Delete? Next" is managed by Terraform in what is called the "State". The state can be shared by leveraging different backends. We can concentrate on describing the resources and the tool to apply them will follow.
    
    
## Let's start (Finally) !

Let's describe our first Terraform resource, and create it in Zentral.

On your machine, start with an empty folder.

First, we need to tell Terraform that we want to use the official [Zentral Terraform provider](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs). So we will create a file with the `.tf` extension (`provider.tf` for example) in the empty folder. We will reference the provider by adding this block:

```terraform
terraform {
  required_providers {
    zentral = {
      source = "zentralopensource/zentral"
    }
  }
}
```

We then need to configure the provider to point it to the right Zentral instance with the right user or service account.

We first need an API token to authenticate with Zentral. We will start with a token attached to your user. In the Zentral admin console, in the top right menu, click on the user icon, and select _Profile_. In your profile, click on the `+` sign in the API token row (If you already have a token, delete it and recreate it, since it cannot be retrieved after creation). Click on the clipboard icon to copy the API token, and save it in your password manager for example.

Once you have the API token, you can finish the configuration of the Zentral provider. In the `.tf` file, add the following block:

```terraform
provider "zentral" {
  base_url = "https://ZENTRAL_FQDN/api/"
  token = "ZENTRAL_API_TOKEN"
}
```

Do not forget to replace `ZENTRAL_FQDN` with the domain name of your Zentral instance (leave `/api/` as path) and `ZENTRAL_API_TOKEN` with the API token you have just created.

Save the `.tf` file.

In the Terminal, go to the folder containing the `.tf` file. This is your working directory for Terraform. You are ready now to initialize Terraform. Use the following command:

```
terraform init
```

**OPTIONAL** In this workshop, you can replace `terraform` with [OpenTofu](https://opentofu.org/) `tofu` in all the examples.

That's it! You are all setup to start managing the Zentral configuration with Terraform.

You can first run the following command to see the changes that your configuration introduces:

```
terraform plan
```

You should see zero changes.

Let's start by adding a tag. In Zentral, a tag is attached to a machine, and is used to scope configuration items. For example, you can distribute a configuration profile to all the machine with the `IT` tag.

This is how you define a Zentral tag with Terraform:

```terraform
resource "zentral_tag" "my-tag" {
  name = "My Tag"
}
```

Terraform concatenates all the definitions find in the `.tf` files in the working directory. So, for your new tag, instead of adding its definition in the `provider.tf` file, use a new `tags.tf` file for example. Save your edits, and run the following command again:

```
terraform plan
```

You should see that Terraform plans to add one tag.

To apply the changes, use the following command:

```
terraform apply
```

That's it.

You can now try to change the tag, add a color, maybe create a second tag. The reference for the tag resource is [here](https://registry.terraform.io/providers/zentralopensource/zentral/latest/docs/resources/tag). The color is expressed like in HTML, for example `ff0000`.

You can cleanup the resources you have created in your Zentral instance with the following command:

```
terraform destroy
```

Now that you have been introduced to Terraform, let's facilitate the collaboration with your workshop colleague by [using some remote state and git](./3_remote_state_and_git.md).
