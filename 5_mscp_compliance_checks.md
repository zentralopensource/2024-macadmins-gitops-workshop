# mSCP compliance checks

You probably know all about the [mSCP project](https://github.com/usnistgov/macos_security).

> The macOS Security Compliance Project is an open source effort to provide a programmatic approach to generating security guidance.

Rules are defined in YAML, and tooling is provided to select the rules you want to enforce, generate scripts to check them, and generate configuration profiles if possible to enforce them.

> [!TIP]
> Clone the mSCP repository.
> 
> Have a look at some rules, like [`os_httpd_disable`](https://github.com/usnistgov/macos_security/blob/main/rules/os/os_httpd_disable.yaml) one for example.
> 
> See how everything is defined in machine format. Locate the check script, but also the fix.

Because the rules are defined in machine format, it is easy to build tools to process them. This is what we did for Zentral. We have built a tool to turn a mSCP baseline into Terraform resources that can be synced with a Zentral instance.

In Zentral, there are 3 types of compliance checks. The inventory checks, the Osquery checks, and the script checks. This tool creates script checks resources. Script checks are distributed to Munki during the standard pre/postflight flow, and each result is uploaded back to Zentral. The compliance checks results are reported in the inventory. There are also aggregated for metrics. Finally, each compliance change triggers an event.

In this section, we will create a baseline (if you still haven't one on hand), and import the compliance checks in Zentral. We will then run them on you test devices, and see what the initial score is!

## Generate a mSCP baseline

### Setup

You need to install python3. It is easy to install it via the XCode command line tools. To trigger the install, simply launch one of the  `git` or `clang` or `gcc` command in a terminal.

Then, clone the mSCP repository, and install the requrired tools:

```bash
git clone https://github.com/usnistgov/macos_security.git

cd macos_security

# git checkout sonoma
git checkout sonoma

# install the python requirements
pip3 install -r requirements.txt --user

# install the ruby requirements
bundle install --binstubs --path mscp_gems
```

### Automatic or Tailored

You can then [generate a baseline](https://github.com/usnistgov/macos_security/wiki/Generate-a-Baseline), either automatically:

```
./scripts/generate_baseline.py -k 800-53r5_moderate
```

Or by [tailoring](https://github.com/usnistgov/macos_security/wiki/Tailoring) one:


```
./scripts/generate_baseline.py -k 800-53r5_moderate -t
```

When tailoring a baseline, it is possible to change the default _Organization Defined Values_ or ODVs. The custome ODVs are written into the `custom/rules` folder.

You should now have a baseline (YAML file) in the `build/baselines` folder, and eventually some ODVs in the `custom/rules` folder.

## Generate the Terraform resources

We will now use the [Zentral tool](https://github.com/zentralopensource/zentral/tree/main/zentral/core/compliance_checks/tools/mSCP) to generate the Terraform resources that we will include in our repository.

### Install the Zentral tool

You need to clone the repository, and install the python requirements.

```
git clone https://github.com/zentralopensource/zentral.git

# install the python requirements
pip3 install -r zentral/core/compliance_checks/tools/mSCP/requirements.txt --user
```

### Generate the `.tf` file

We can now run the tool to generate the Terraform resources for your mSCP baseline.

**You might need to customize the following command!**

- Replace the `800-53r5_moderate.yaml` filename with the actual value
-  This commands works when launched from a folder containing the `zentral/` and `macos_security/` cloned repositories. You may have cloned them somewhere else in your environment.

```
python3 zentral/zentral/core/compliance_checks/tools/mSCP/build_tf_script_checks.py \
        ./macos_security/build/baselines/800-53r5_moderate.yaml \
        ./macos_security \
        --min-os-version 14 \
        --max-os-version 15 \
        munki_script_checks.tf
```

The output is verbose, and it is OK if some rules are skipped or ignored. Not all the rules in the mSCP project have scripts. Some of them are general recommendations for which no configuration exist in macOS.


> [!TIP]
> 
> Open the `munki_script_checks.tf` that was generated. Look at the resource definitions. Try to find the corresponding rules in the mSCP repository, and verify that the scripts are the same.


## Add the generated TF resources to Zentral

We want to import the generated TF resources into Zentral. We will use our Terraform GitHub pipeline for it.

> [!TIP]
> 
> Copy the `munki_script_checks.tf` file into your repository.
> 
> Run `terraform fmt` to format the script.
> 
> Create a new branch, commit the file, push the branch, and create a Pull request.
> 
> Verify the output of the Terraform plan in the PR conversation.
> 
> Have one of your team mate do a code review
> 
> When everything is fine, merge the PR (Your pipeline may fail because the generated file is not correctly formatted. See `terraform fmt`.)
> 
> Go to Zentral, open the _Munki > Script checks_ section and see the imported scripts.

