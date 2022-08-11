from collections import defaultdict

from infrahub.checks import InfrahubCheck

class InfrahubCheckBackboneLinkRedundancy(InfrahubCheck):

    query = """
        query ($branch: String!) {
            circuit(role__name__value: "backbone") {
                id
                circuit_id {
                    value
                }
                vendor_id {
                    value
                }
                status {
                    name {
                        value
                    }
                }
                endpoints {
                    site {
                        id
                        name {
                            value
                        }
                    }
                    connected_interface {
                        enabled {
                            value
                        }
                    }
                }
            }
        }
    """

    def validate(self):

        site_id_by_name = {}

        backbone_links_per_site = defaultdict(lambda: defaultdict(int))

        for circuit in self.data["data"]["circuit"]:
            circuit_id = circuit["id"]
            status = circuit["status"]["name"]["value"]

            for endpoint in circuit["endpoints"]:
                site_name = endpoint["site"]["name"]["value"]
                site_id_by_name[site_name] = endpoint["site"]["id"]
                backbone_links_per_site[site_name]["total"] += 1
                if endpoint["connected_interface"]["enabled"]["value"] and status == "active":
                    backbone_links_per_site[site_name]["operational"] += 1

        for site_name, site in backbone_links_per_site.items():
            if site.get("operational", 0) / site["total"] < 0.6:
                self.log_error(
                    message=f"{site_name} has less than 60% of backbone circuit operational ({site.get('operational', 0)}/{site['total']})",
                    object_id=site_id_by_name[site_name],
                    object_type="site",
                )

INFRAHUB_CHECKS = [InfrahubCheckBackboneLinkRedundancy]
