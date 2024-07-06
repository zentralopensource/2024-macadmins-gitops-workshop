# Remote state and Git

## The importance of the remote state backend

As you may have noticed, when multiple users apply similar Terraform resources to the same backend, it may lead to some errors and issues.

The main reason is that with the simple setup we have used so far, the Terraform state is not shared. It is stored locally in a file called `terraform.tfstate`

> [!TIP]
> Have a look in your working directory. Peek inside the file (JSON data structure) to see the resources you have created.

When used without a remote backend for the state, Terraform only sees what has changed locally. If something is absent from the local state, it will try to create it, even if it has already been created somewhere else.

This is why it is **important** to setup a [remote state backend](https://developer.hashicorp.com/terraform/language/state/remote).

Depending on the remote backend, you could even have state locking, meaning that before applying changes, the state will be locked, preventing some important issues.

A remote backend is also probably more robust than a file on a laptop. With AWS S3 for example, you could also enable automatic object versioning to keep older versions of the state.

The state also should be kept separated from the resource definitions (the code). The state may contain sensitive information. You also want to be able to share a repository without sharing the state of your deployments. You may also have 2 separate states (staging and production for example) based on the same code.

## Built-in Zentral backend

Because this is so important for a successful Terraform workflow, and because we really want to help our customers, a remote Terraform state backend is available in each deployment of Zentral.

> [!TIP]
> In the Zentral console, click on the three vertical dots menu item in the top right corner, and select _Terraform_.
>
> You should see that there is already one state: `starter_kit`.
>
> If you click on the link, you can see that this state has one version, and you can also see the configuration for it.

To facilitate the setup, the Zentral state backend uses the same API token than the rest of the Zentral API – but it must be configured slightly differently in Terraform than the provider.

You must be wondering… Why does a Terraform state already exist in our instance?

For each Zentral Cloud tenant, we pre-configure the instances with one of the standard TF setup. For the instances used in this workshop, we have deployed the following Terraform setup:

```
https://github.com/zentralopensource/zentral-cloud-tf-starter-kit
```

We have stored the state resulting from this deployment in Zentral itself, so that you can pick up from where we stopped.

> [!TIP]
> Have a look at the definitions in the GitHub repository above and see if you can find the corresponding resources in the Zentral console on your instance.

## New working dir with remote state

So, let's setup a new Terraform working dir, based on the starter kit, and configure your Zentral instance as the remote state backend.

> [!TIP]
> Download a [ZIP archive the startup kit](https://github.com/zentralopensource/zentral-cloud-tf-starter-kit/archive/refs/heads/main.zip) repository. **Do not clone it**, since you will be creating a new repository.
>
>  Unzip it into a new working directory on your machine.
> 
> In the `provider.tf` file, replace the `// BACKEND PLACEHOLDER` with the **partial** configuration block at the bottom of the `starter_kit` state detail page in your Zentral instance.

The backend is only **partially** configured. We did that to avoid writting secrets in the code. The `username` and `password` attributes are required, but will be set during the initialization of the working directory.

Let's first setup the shell environment with some variables required to apply the configuration

```bash
export ZTL_USERNAME=your-username
export ZTL_API_TOKEN=your-api-token
export TF_VAR_fqdn="your-instance-name.zentral.cloud"
export TF_VAR_api_token=$ZTL_API_TOKEN
```

The last two variables have a special prefix. Terraform recognizes them and uses them as values when planing the deployment.

> [!TIP]
> Have a look again in the `provider.tf` file and in the `variables.tf` file. You will see the definition of `api_token` and `fqdn` and how we use them.

You might be wondering why we haven't used the `fqdn` variable when defining the backend. Well, it is not possible to have a dynamic backend configuration!

> Initialize your working directory by running the `terraform init` command at the bottom of the `starter_kit` state detail page in your Zentral instance.
> 
> **Do not forget the extra backend options to complement the partial configuration**. 

The remote backend is configured now. The [official Zentral terraform provider](https://registry.terraform.io/providers/zentralopensource/zentral/latest) has been downloaded too. This is the plugin that enables Terraform to talk to a Zentral instance. It translates the resources between the Zentral json format and the internal Terraform state representation. It also implements the Terraform CRUD operations using the Zentral API.

> [!TIP]
> 
> Run `terraform plan`


You should see `No changes`. The Terraform `starter_kit` state in Zentral, and the resource definitions in this working directory are in sync.

If you run `terraform apply`, nothing will happen.

Now that you have the current Terraform configuration, and the corresponding remote state, let's [setup a GitHub repository to start collaborating with your team mate](./4_github_repository_and_actions.md).
