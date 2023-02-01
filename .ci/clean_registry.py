import os

from ghapi.all import GhApi
from ghapi.core import print_summary
from ghapi.page import paged

org_str = "pyansys"
pck_str = "geometry"
valid_tags = ["windows-latest", "windows-latest-unstable", "linux-latest", "linux-latest-unstable"]

api = GhApi(debug=print_summary, token=os.getenv("PACKAGE_DELETION_TOKEN"))

paged_packages = paged(
    api.packages.get_all_package_versions_for_package_owned_by_org,
    org=org_str,
    package_name=pck_str,
    package_type="container",
    state="active",
    per_page=100,
)

# Loop over all pages
for page in paged_packages:
    for package in page:
        # Check if the given package should be deleted
        package_tags = package.metadata.container.tags
        delete = True
        for tag in package_tags:
            if tag in valid_tags:
                delete = False
                break

        # In case it should, delete it
        if delete:
            print("Deleting:" + package)
            api.packages.delete_package_version_for_org(
                org=org_str,
                package_name=pck_str,
                package_type="container",
                package_version_id=package["id"],
            )
