from unittest import TestCase

from simple_solver import Watchlist, SimpleSATSolver
from utils import Clause, Literal


class TestWatchlist(TestCase):

    def test_setup_watchlist(self):
        # Given
        clauses = [Clause.from_string(r) for r in ('1 2 3', '2 3 4')]
        watchlist = Watchlist()

        # When
        for clause in clauses:
            watchlist.add_clause(clause)

        # Then
        l = watchlist._watchlist
        watched_clauses = [queue[0] for queue in l.values()]
        self.assertItemsEqual(watched_clauses, clauses)
        self.assertItemsEqual(l.keys(), [clause[0] for clause in clauses])

    def test_update_consistent(self):
        # Given
        clauses = [
            Clause.from_string(r) for r in ('1 2 -3', '2 3', '2')
        ]
        watchlist = Watchlist(clauses)
        assignments = {'1': None, '2':  None, '3':  None}
        false_literal = Literal('1', is_conjugated=False)
        reassigned_clause = watchlist._watchlist[false_literal][0]

        # When
        assignments['1'] = False
        status = watchlist.update(false_literal, assignments)

        # Then
        self.assertTrue(status)
        self.assertEqual(len(watchlist._watchlist[false_literal]), 0)
        self.assertIn(reassigned_clause,
                      watchlist._watchlist[Literal('2', False)])

    def test_update_inconsistent(self):
        # Given
        clause = Clause.from_string('1 2')
        watchlist = Watchlist([clause])
        assignments = {'1': None, '2': False}
        false_literal = Literal('1', is_conjugated=False)
        original_watchlist = watchlist._watchlist.copy()

        # When
        assignments['1'] = False
        status = watchlist.update(false_literal, assignments)

        # Then
        self.assertFalse(status)
        self.assertDictEqual(watchlist._watchlist, original_watchlist)


class TestSimpleSATSolver(TestCase):

    def test_simple_consistent(self):
        # Given
        clauses = [
            Clause.from_string(s) for s in
            ['1 -2 3', '-1 3', '-3']
        ]
        solver = SimpleSATSolver(clauses)

        # When
        solutions = list(solver.solve())

        # Then
        self.assertItemsEqual(solutions,
                              [{'1': False, '2': False, '3': False}])

    def test_simple_consistent_multiple(self):
        # Given
        clauses = [
            Clause.from_string(s) for s in
            ['1 -2 3', '-1 3']
        ]
        solver = SimpleSATSolver(clauses)

        # When
        solutions = list(solver.solve())

        # Then
        self.assertItemsEqual(
            solutions,
            [{'1': True, '3': True, '2': True},
             {'1': True, '3': True, '2': False},
             {'1': False, '3': True, '2': True},
             {'1': False, '3': True, '2': False},
             {'1': False, '3': False, '2': False}])

    def test_simple_inconsistent(self):
        # Given
        clauses = [
            Clause.from_string(s) for s in
            ['-1 -2 -3', '1', '2', '3']
        ]
        solver = SimpleSATSolver(clauses)

        # When
        solutions = list(solver.solve())

        # Then
        self.assertEqual(len(solutions), 0)
