def levenshtein_distance(first: str, second: str) -> int:

    first = first.strip().lower()
    second = second.strip().lower()

    rows = len(first) + 1
    columns = len(second) + 1

    matrix = [[0] * columns for _ in range(rows)]

    for row in range(rows):
        matrix[row][0] = row

    for column in range(columns):
        matrix[0][column] = column

    for row in range(1, rows):
        for column in range(1, columns):

            if first[row - 1] == second[column - 1]:
                cost = 0
            else:
                cost = 1

            deletion = matrix[row - 1][column] + 1
            insertion = matrix[row][column - 1] + 1
            substitution = matrix[row - 1][column - 1] + cost

            matrix[row][column] = min(
                deletion,
                insertion,
                substitution
            )

    return matrix[rows - 1][columns - 1]


def similarity_percentage(first: str, second: str) -> float:

    first = first.strip().lower()
    second = second.strip().lower()

    longest_length = max(len(first), len(second))

    if longest_length == 0:
        return 100.0

    distance = levenshtein_distance(first, second)

    percentage = (1 - distance / longest_length) * 100

    return round(percentage, 2)


# Run tests only when this file is executed directly
if __name__ == "__main__":

    official = "mekongfinance.example"
    candidate = "mekong-finance.example"

    print("Edit Distance:",
          levenshtein_distance(official, candidate))

    print("Similarity:",
          similarity_percentage(official, candidate), "%")