# Discover your Zentral instance

We have prepared Zentral instances for this workshop. They are deployed in our SaaS environment, Zentral Cloud.

## Log into your instance

1. Use the info (URL, user, password) on the piece of paper to log into your Instance.

2. Change the email, username and password of the default user.
    
    **OPTIONAL** configure MFA

3. Invite your workshop partner(s) to the instance.
    
    Click on the three vertical dots in the top right corner, then open the _Users_ view. Click on the _Email_ icon in the top right corner. Submit the form.

    They will receive a password reset email.

4. Promote your workshop partner to _superuser_.

    In the Users list, pick the newly created user, edit them, and promote them to superuser.

    _We have a fine grained RBAC system in Zentral, but to speed-up things for this workshop, we will use superusers, at least at first. In Zentral, a superuser automatically gets all the permissions. The API token associated with a superuser also has all the permissions._

## Quick tour of your Zentral instance

We have pre-configured your Zentral instance, and activated the main modules:

### The inventory

This is where all the information about the devices is presented. All the agents and modules in Zentral contributes to the inventory.

### MDM

The Apple MDM, for … MDM stuff.

### Munki/Monolith

Those two modules communicate with the [Munki](https://github.com/munki/munki) agent. We have picked Munki to manage 3rd party software with Zentral. It is  the ideal companion to the Apple MDM. _Monolith_ is the dynamic layer on top of a repository that enables the scoping of packages with tags. _Munki_ is the module directly involved with Munki via the pre/post flight scripts. It enables the shipping of the reports, and also the compliance checks based on scripts. But we will come back to that later during the day.

### Osquery

[Osquery](https://osquery.io/) is a well established agent that gives exhaustive and precise information about a device. With this module, Zentral can manage the dynamic configuration of the agents, distribute real-time queries, and collect all the results and logs.

### Santa

The [Google Santa agent](https://santa.dev/) is the application allow/block listing tool of choice for the Mac. Zentral can distribute dynamic rules to the fleet. It also collects and aggregates the events shipped by the agents.

### Elasticsearch / Kibana

In the backend, the events are stored in Elasticsearch (or OpenSearch in permium deployments). Each Cloud deployment of Zentral gets a separate event store. You can get raw access to the event with Kibana.

### Prometheus

Zentral exports metrics about its different components and the modules for [Prometheus](https://prometheus.io/). We deploy a Prometheus instance for all the tenants to collect the metrics over time. You can access and query the raw data if you want.

### Grafana

Finally, we have also a [Grafana](https://grafana.com/) instance in our Cloud tenants. This is the perfect tool to build custom dashboards bringing together the metrics collected with Prometheus and the events stored in Elasticsearch.

## Enroll your test device or VM

To get started, enroll your test device or VM in Zentral. To speed things up, we have already signed the MDM APNS certificate and we have configured an OTA enrollment.

> [!TIP]
> Go to _MDM > Enrollments_.
> 
> You should see a _Default_ OTA enrollment.
> 
> Click on the link (_Default_) to see the details.

MDM enrollments in Zentral connects a SCEP configuration, a Push certificate and a blueprint. A blueprint is a selection of _Artifacts_ (Configuration profiles, Enterprise applications) and other settings (FileVault, Recovery Lock, …).

_An enrollment It is usually configured with an Identity Provider (Realm in Zentral) for authentication during Automatic Device Enrollment or OTA Enrollment. With authentication, a public link to the OTA profile is available, and the end users must authenticate before they can download the profile._

> [!TIP]
> Use the download button to download the profile.
> 
> Install the profile in your test device or your VM:
> 
> Open the Settings app, look for the `profiles` panel, and click on the `Zentral MDM` profile.

After a 1 or 2 minutes, a dialog should be displayed with a list of packages being installed. As you can see, we have pre-configured the blueprint with all the required configuration to enroll Munki, Osquery and Santa.

## Browse the device information in Zentral

> [!TIP]
> In the Zentral console, go to the _Inventory > Machines_ section (top left corner).
>
> You should at least see one source: _MDM_.
>
> Select it, and you should be able to find your test devices in the list.
> 
> Click on their serial number to see a detailed view.

Zentral has a unified inventory. By now, you should see multiple tabs for the different agents that contribute their inventory data.

> [!TIP]
> In the _Events_ tab of the machine page, you will be able to see all the events attached to it.
>
> Use the event type filter to see only the MDM requests.
> Click on the _Elasticsearch_ button to view the same events in Kibana.

This is it. Now that you have familiarized yourselves with Zentral, let's see how we can leverage it to manage macOS clients with GitOps.

Next part: [GitOps introduction](./2_gitops_intro.md)
