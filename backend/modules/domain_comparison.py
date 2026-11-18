def normalize_domain(domain: str) -> str:
    return domain.strip().lower()


def compare_domains(official_domain: str, candidate_domain: str) -> bool:

    official = normalize_domain(official_domain)
    candidate = normalize_domain(candidate_domain)

    return official == candidate


# Run this section only when executing this file directly
if __name__ == "__main__":

    print("=== KCG Domain Comparison ===")

    official_domain = input("Enter official domain: ")
    candidate_domain = input("Enter candidate domain: ")

    result = compare_domains(official_domain, candidate_domain)

    if result:
        print("Result: Exact domain match.")
    else:
        print("Result: Domains are different.")