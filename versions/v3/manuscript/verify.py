from fractions import Fraction
from itertools import product
import json


def scalar(real=0, imaginary=0):
    return (Fraction(real), Fraction(imaginary))


def plus(left, right):
    return (left[0] + right[0], left[1] + right[1])


def times(left, right):
    return (left[0] * right[0] - left[1] * right[1],
            left[0] * right[1] + left[1] * right[0])


def conjugate(value):
    return (value[0], -value[1])


def matrix(rows):
    return [[entry if isinstance(entry, tuple) else scalar(entry) for entry in row]
            for row in rows]


def identity(dimension):
    return matrix([[int(row == column) for column in range(dimension)]
                   for row in range(dimension)])


def multiply(left, right):
    return [[sum_scalars(times(left[row][middle], right[middle][column])
                         for middle in range(len(right)))
             for column in range(len(right[0]))] for row in range(len(left))]


def sum_scalars(values):
    total = scalar()
    for value in values:
        total = plus(total, value)
    return total


def adjoint(value):
    return [[conjugate(value[row][column]) for row in range(len(value))]
            for column in range(len(value[0]))]


def scaled(value, coefficient):
    return [[times(entry, coefficient) for entry in row] for row in value]


def subtract(left, right):
    return [[plus(left[row][column], times(scalar(-1), right[row][column]))
             for column in range(len(left[0]))] for row in range(len(left))]


def trace(value):
    return sum_scalars(value[index][index] for index in range(len(value)))


def zero_matrix(dimension):
    return matrix([[0] * dimension for row in range(dimension)])


def inter_gate(dimension, slot):
    rotation = identity(dimension)
    left = slot % dimension
    right = (slot + 1) % dimension
    rotation[left][left] = scalar(Fraction(3, 5))
    rotation[right][right] = scalar(Fraction(3, 5))
    rotation[left][right] = scalar(Fraction(-4, 5))
    rotation[right][left] = scalar(Fraction(4, 5))
    permutation = matrix([[int(column == (row + slot) % dimension)
                           for column in range(dimension)] for row in range(dimension)])
    result = multiply(permutation, rotation)
    assert multiply(adjoint(result), result) == identity(dimension)
    return result


def run(workspace, signs, negated):
    dimension = 2 * workspace
    result = inter_gate(dimension, 0)
    for slot, sign in enumerate(signs, 1):
        query = zero_matrix(dimension)
        for index in range(dimension):
            query[index][index] = scalar(0, sign * (-1 if negated else 1)
                                         * (1 if index % 2 == 0 else -1))
        result = multiply(multiply(inter_gate(dimension, slot), query), result)
    return result


def channel_on_basis(value, row, column):
    return [[times(value[output_row][row], conjugate(value[output_column][column]))
             for output_column in range(len(value))] for output_row in range(len(value))]


def main():
    imaginary = scalar(0, 1)
    negative_imaginary = scalar(0, -1)
    density = scaled(matrix([[1, 1], [1, 1]]), scalar(Fraction(1, 2)))
    first_target = matrix([[1, 0], [0, imaginary]])
    second_target = matrix([[imaginary, 0], [0, 1]])
    first = multiply(multiply(first_target, density), adjoint(first_target))
    second = multiply(multiply(second_target, density), adjoint(second_target))
    expected_first = scaled(matrix([[1, negative_imaginary], [imaginary, 1]]), scalar(Fraction(1, 2)))
    expected_second = scaled(matrix([[1, imaginary], [negative_imaginary, 1]]), scalar(Fraction(1, 2)))
    assert first == expected_first and second == expected_second
    for state in [density, first, second]:
        assert adjoint(state) == state
        assert trace(state) == scalar(1)
        assert multiply(state, state) == state
    assert multiply(first, second) == zero_matrix(2)
    difference = subtract(first, second)
    assert multiply(adjoint(difference), difference) == identity(2)
    assert trace(identity(2)) == scalar(2)
    coefficient = matrix([[0, negative_imaginary], [imaginary, 0]])
    assert multiply(adjoint(coefficient), coefficient) == identity(2)
    cases = 0
    for workspace in [1, 2, 3]:
        for query_count in range(5):
            for signs in product([-1, 1], repeat=query_count):
                positive = run(workspace, signs, False)
                negative = run(workspace, signs, True)
                assert negative == scaled(positive, scalar((-1) ** query_count))
                for row, column in product(range(2), repeat=2):
                    assert channel_on_basis(positive, row, column) == channel_on_basis(negative, row, column)
                cases += 1
    pi_lower_quarter = sum((Fraction((-1) ** index, 2 * index + 1)
                            for index in range(8)), Fraction(0))
    assert pi_lower_quarter == Fraction(33976, 45045)
    assert pi_lower_quarter > Fraction(3, 4)
    report = {
        'status': 'pass',
        'arithmetic': 'Gaussian rational pairs of Python Fraction; exact, without rounding',
        'fixed_witness': {'dimension': 2, 't': '1/2', 'delta': '1/2',
                          'normalized_orthogonal_target_projectors': True,
                          'trace_norm_separation': '2',
                          'incompatible_requested_uniform_error': '1/4'},
        'coefficient_identity': 'Y=[[0,-i],[i,0]]; Y^*Y=I_2',
        'finite_circuits': {'query_counts': [0, 1, 2, 3, 4],
                            'workspace_dimensions': [1, 2, 3],
                            'sign_words': 'all at each listed query count',
                            'cases': cases,
                            'gate_family': 'slot-dependent exact 3/5,4/5 plane rotations and cyclic permutations',
                            'channel_basis_inputs_per_case': 4,
                            'verified_identity': 'A(-U)=(-1)^N A(U); initialized full-output channels coincide'},
        'pi_certificate': {'arctan_lower_partial_sum': str(pi_lower_quarter),
                           'comparison': '33976/45045 > 3/4',
                           'analytic_implication': 'alternating arctan series at 1 gives 3 < pi < 4'},
        'proof_scope': 'Finite checks for the fixed witness and listed circuits; the all-circuit and all-t conclusions have written proofs in note.tex.'
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
