from fractions import Fraction
from itertools import product
import json

from verify import (
    adjoint, channel_on_basis, inter_gate, multiply,
    scalar, scaled, subtract, trace, zero_matrix,
)


def diagonal(values):
    result = zero_matrix(len(values))
    for index, value in enumerate(values):
        result[index][index] = value
    return result


def circuit(system_dimension, workspace_dimension, signs, negative):
    total_dimension = system_dimension * workspace_dimension
    oracle_values = [scalar(1), scalar(-1)] + [scalar(1)] * (system_dimension - 2)
    oracle = diagonal(oracle_values)
    if negative:
        oracle = scaled(oracle, scalar(-1))
    result = inter_gate(total_dimension, 0)
    for slot, sign in enumerate(signs, 1):
        system_query = adjoint(oracle) if sign < 0 else oracle
        query = zero_matrix(total_dimension)
        for index in range(total_dimension):
            query[index][index] = system_query[index % system_dimension][index % system_dimension]
        result = multiply(multiply(inter_gate(total_dimension, slot), query), result)
    return result


def main():
    witness_dimensions = []
    for dimension in [2, 3, 4]:
        positive = diagonal([scalar(1), scalar(-1)] + [scalar(1)] * (dimension - 2))
        negative = scaled(positive, scalar(-1))
        root_positive = diagonal([scalar(1), scalar(0, 1)] + [scalar(1)] * (dimension - 2))
        root_negative = diagonal([scalar(0, 1), scalar(1)] + [scalar(0, 1)] * (dimension - 2))
        assert multiply(root_positive, root_positive) == positive
        assert multiply(root_negative, root_negative) == negative
        density = zero_matrix(dimension)
        for row, column in product(range(2), repeat=2):
            density[row][column] = scalar(Fraction(1, 2))
        first = multiply(multiply(root_positive, density), adjoint(root_positive))
        second = multiply(multiply(root_negative, density), adjoint(root_negative))
        assert trace(first) == scalar(1) and trace(second) == scalar(1)
        assert multiply(first, second) == zero_matrix(dimension)
        difference = subtract(first, second)
        support = diagonal([scalar(1), scalar(1)] + [scalar()] * (dimension - 2))
        assert multiply(adjoint(difference), difference) == support
        assert trace(support) == scalar(2)
        assert subtract(support, first) == second
        witness_dimensions.append(dimension)

    cases = 0
    for dimension, workspace in product([2, 3, 4], [1, 2]):
        for count in range(4):
            for signs in product([-1, 1], repeat=count):
                positive = circuit(dimension, workspace, signs, False)
                negative = circuit(dimension, workspace, signs, True)
                assert negative == scaled(positive, scalar((-1) ** count))
                for row, column in product(range(dimension), repeat=2):
                    assert channel_on_basis(positive, row, column) == channel_on_basis(
                        negative, row, column)
                cases += 1

    gaps = [Fraction(1, 8), Fraction(1, 2), Fraction(3, 4), Fraction(7, 8)]
    for gap in gaps:
        assert 0 < gap < 1 and gap + 1 < 2
        assert [gap, gap + 1] == sorted([gap + 1, gap])

    polynomial_examples = 0
    for first, second, shift in product([Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)], repeat=3):
        quadratic_difference = ((first + shift) ** 2 - first ** 2
                                - (second + shift) ** 2 + second ** 2)
        assert quadratic_difference == 2 * shift * (first - second)
        for slope in range(-3, 4):
            affine_difference = (slope * (first + shift) - slope * first
                                 - slope * (second + shift) + slope * second)
            assert affine_difference == 0
        polynomial_examples += 1

    report = {
        'status': 'pass',
        'arithmetic': 'Exact Gaussian rational pairs and rational arithmetic; Python standard library',
        'system_dimensions': witness_dimensions,
        'gap_examples_in_units_of_pi': [str(value) for value in gaps],
        'spectral_identity': 'H+ entries delta and delta+pi; H- entries swapped; delta+pi<2*pi',
        'square_root_projectors': 'Orthogonal rank-one targets; their sum is the first-two-coordinate projector',
        'square_root_pure_output_bound': {'squared_lower_bound': '2', 'lower_bound': 'sqrt(2)'},
        'ordered_circuits': {'system_dimensions': [2, 3, 4], 'workspace_dimensions': [1, 2],
                             'query_counts': [0, 1, 2, 3], 'sign_words': 'all at each listed query count',
                             'gate_family': 'Exact 3/5,4/5 plane rotations and cyclic permutations',
                             'cases': cases, 'identity': 'A(-U)=(-1)^N A(U)'},
        'polynomial_examples': {'triples': polynomial_examples, 'affine_integer_slopes': list(range(-3, 4)),
                                'quadratic_finite_difference': '2*h*(x-y)'},
        'proof_scope': 'Finite matrix and polynomial identities only; all-parameter bounds and the C1 classification have written proofs in note.tex.',
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
