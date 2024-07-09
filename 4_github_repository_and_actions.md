# GitHub repository & actions

## The repository

We are finally ready to put the Git into GitOps. First we need a GitHub repository to push the code to.

> [!TIP]
>
> Create a [GitHub repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories)
>
> Use the suggested commands to make your first commit in your latest Terraform working directory and push it to GitHub.
>
> To authenticate with GitHub, here is a [doc](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github).

You then need to add your team mates as collaborators, so that they can work on the code, and have access to the repository variables and secrets.

GitHub enables more granular access within organizations, but this is out of scope for this workshop. If you do not already have an organization or a paid GitHub account, keep it simple and create a public personal repository.

> [!TIP]
>
> Invite your team mates as [collaborators on the repository](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-access-to-your-personal-repositories/inviting-collaborators-to-a-personal-repository#inviting-a-collaborator-to-a-personal-repository)


## The GitHub actions

We have configuration as code, we have a repository to manage the code, we have a tool to apply the changes to the server, but the last piece of the GitOps workflow is missing.

**We need a CI/CD pipeline** to **automatically** see what changes we introduce, and apply them to the instance when we are ready.

Every established source management product (GitLab, GitHub, …) has a pipeline functionality. You can also configure dedicated CI/CD products to integrate with your source management product. For this workshop, we will simply use [GitHub actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions#the-components-of-github-actions).

In this repository, we have included an example of a [`.github` folder](./assets/4_dot-github/), containing a single [`tf-plan-apply.yml`](./assets/4_dot-github/workflows/tf-plan-apply.yml) workflow.

A workflow is a collection of jobs, themselves composed of different tasks run sequentially. Workflows can be triggered by the GitHub events, like a PR creation or a PR merge into a specific branch.

> [!TIP]
> Open the [`tf-plan-apply.yml`](./assets/4_dot-github/workflows/tf-plan-apply.yml) file.
>
> Identify the events that are triggering this workflow.
>
> Identify the 2 different jobs.
>
> Try to find the tasks that we have just run in the terminal to initialize the working directory, and plan/apply the configuration.
>
> Try to find how the terraform plan is passed between the first and the second job.

Now that we understand better how the CI/CD pipeline is built, let's add it to our repository.

> [!TIP]
>  Copy the [`./assets/4_dot-github`](./assets/4_dot-github) folder to a `.github` folder in your repository.

Before we commit the changes, let's configure the GitHub repository [variables](https://docs.github.com/en/actions/learn-github-actions/variables) and [secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions). Remember how we exported some environment variables in the precedent section of the workshop ? The same information is required to initialize the Terraform working directory in the jobs, and set the Terraform variables.

We will configure 2 **repository** variables and 1 **repository** secret:

|Name|Secret?|Value|
|---|---|---|
|`ZTL_FQDN`||your-instance.zentral.cloud|
|`ZTL_USERNAME`||The Zentral username associated with the API token|
|`ZTL_API_TOKEN`|✅|The Zentral API token|

> [!TIP]
>  Go to your repository in GitHub, open the _Settings > Secrets and variables > actions_ section.
>
>  In the _Secrets_ tab, add a the new `ZTL_API_TOKEN` secret.
>
> In the _Variables_ tab, add `ZTL_FQDN` and `ZTL_USERNAME`

We are ready to create or first pull request!

> [!TIP]
> Create a new branch in your code.
>
> Commit the `.github` folder.
>
> Push the new branch to GitHub.
>
> Open a Pull Request.

You should see the _Terraform Plan/Apply_ workflow being triggered in the PR user interface. After a while it should turn green. If there is an error, click on the _Details_ link, and read the logs. It could be that the variables or the secret were misconfigured.

You should also see that the Terraform Plan has been added to the PR conversation. Since the last commit only added the workflow and no extra resources, you should see `No changes` when you click on the _Click to expand_ link.

Now that the worklow was successful, and that we have reviewed the changes in introduce, we are ready to merge the PR into the `main` branch.

> [!TIP]
> [Merge the PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request) into the `main` branch.
>
> Open the `Actions` tab in your repository. You should see a new workflow being triggered.

We now have a well defined workflow for you to collaborate within your team. Changes are proposed via pull requests. A Terraform plan will be calculated to display what changes the PR is introducing in the Zentral instance. Once everything is OK, the PR will be merged and the changes will be applied in the Zentral instance.

> [!TIP]
> Use the GitHub GUI or your code editor to change the name of the Santa configuration via a PR.
>
> Review the plan, Merge the PR.
>
> Open the `Actions` tab in your repository after the PR has been merged. Notice that this time, the 2 jobs (Plan & Apply) are running.
>
> Verify in your Zentral instance that the Santa configuration has the new name.

## Branch protection

You may have notice that you can still push the changes directly into the `main` branch, and that you do not need to do a code review before merging the pull request. We need to create a [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule) rule in the GitHub repository.

> [!TIP]
> In the _Settings > Rules > Rulesets_ section of your GitHub repository, click on the _New ruleset_ button.
>
> Pick a name (`main` for example)
>
> Add the default branch as target
>
> Select _Require a pull request before merging_
>
> - Set the _Required approvals_ option to `1`.
> - Select _Dismiss stale pull request approvals when new commits are pushed_
> - Select _Require approval of the most recent reviewable push_
>
> Select _Require status checks to pass_
>
> - Select _Require branches to be up to date before merging_
> - In the _Add checks_ dropdown, search for Terraform plan, and select it.
>
> Save your changes

We have now protected the `main` branch. The workflow we have setup is now enforced, except for the administrators of the repository who can still bypass some of the rules. Let's verify that the protection works.


> [!TIP]
> Try to make a change in one of the files in GitHub, you should see that you need to create a new branch.
>
> Once you create a pull request, you should see that a review is required, and that the Terraform plan check is required too.

We can now finally work on the configuration of our macOS clients. Let's start by [adding some compliance checks](./5_mscp_compliance_checks.md).
