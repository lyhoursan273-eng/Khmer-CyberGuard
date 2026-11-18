import dns.resolver
import dns.exception


def check_dns_records(domain: str) -> dict:

    domain = domain.strip().lower().rstrip(".")

    if not domain or " " in domain or "/" in domain:
        raise ValueError("Invalid domain input.")

    resolver = dns.resolver.Resolver()

    # Set a short DNS timeout
    resolver.timeout = 2
    resolver.lifetime = 2

    record_types = ["A", "AAAA", "MX", "NS"]

    results = {}

    for record_type in record_types:

        try:
            answer = resolver.resolve(
                domain,
                record_type
            )

            records = [
                record.to_text()
                for record in answer
            ]

            if record_type == "MX" and records == ["0 ."]:
                status = "null_mx"
            else:
                status = "found"

            results[record_type] = {
                "status": status,
                "records": records
            }

        except dns.resolver.NXDOMAIN:
            results[record_type] = {
                "status": "nxdomain",
                "records": []
            }

        except dns.resolver.NoAnswer:
            results[record_type] = {
                "status": "no_record",
                "records": []
            }

        except dns.exception.Timeout:
            results[record_type] = {
                "status": "timeout",
                "records": []
            }

        except dns.resolver.NoNameservers:
            results[record_type] = {
                "status": "no_nameservers",
                "records": []
            }

    return results


# Test DNS enrichment
if __name__ == "__main__":

    test_domain = "samplebank.example"

    print("=== KCG DNS ENRICHMENT ===")
    print("Testing domain:", test_domain)

    dns_results = check_dns_records(test_domain)

    for record_type, information in dns_results.items():

        print("\nRecord:", record_type)
        print("Status:", information["status"])
        print("Records:", information["records"])