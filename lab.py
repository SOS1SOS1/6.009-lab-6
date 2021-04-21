#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def update_formula(formula, new_assignment):
    """
    Takes in a CNF formula and a new assignment, like ('a', True)
    Returns the updated CNF formula and any implications of the new_assignment
    >>> update_formula([ [('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], [('d', False), ('e', True), ('a', True), ('g', True)], [('h', False), ('c', True), ('a', False), ('f', True)] ], { 'a': True } )
    [[('f', True)], [('h', False), ('c', True), ('f', True)]]
    >>> update_formula([ [('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], [('d', False), ('e', True), ('a', True), ('g', True)], [('h', False), ('c', True), ('a', False), ('f', True)] ], { 'a': False } )
    [[('b', True), ('c', True)], [('d', False), ('e', True), ('g', True)]]
    >>> update_formula([ [('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], [('d', False), ('e', True), ('a', True), ('g', True)], [('h', False), ('c', True), ('a', False), ('f', True)] ], { 'a': True, 'f': True } )
    True
    >>> update_formula([ [('a', True), ('b', True), ('c', True)], [('a', False), ('f', True)], [('d', False), ('e', True), ('a', True), ('g', True)], [('h', False), ('c', True), ('a', False), ('f', True)] ], { 'a': True, 'f': False } )
    False
    """
    new_formula = []
    for clause in formula:
        new_clause = []
        num_false = 0
        for literal in clause:
            variable = literal[0]
            value = literal[1]
            if variable in new_assignment:
                if new_assignment[variable] == value:
                    # entire clause can be removed since it evalutes to True if one of the literal matches a new assignment
                    new_clause = []
                    break
                else:
                    # remove this literal from the clause since it is False
                    num_false += 1
                    if num_false == len(clause):
                        # clause evaluated to False and thus the entire formula is False
                        return False
            else:
                # keep this literal in the clause
                new_clause.append(literal)
        if new_clause:
            new_formula.append(new_clause)
    if not new_formula:
        return True
    return new_formula

def satisfying_assignment(formula, assignment=None):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if not assignment:
        assignment = {}

    # loops through formula looking for unit clauses and propagates their consequences through the 
    # formula until aren't anymore unit clauses in the formula
    i = 0
    while i < len(formula):
        if len(formula[i]) == 1:
            literal = formula[i][0]
            assignment[literal[0]] = literal[1]
            formula = update_formula(formula, { literal[0]: literal[1] })
            if formula == True:
                return assignment
            elif formula == False:
                return None
            i = 0
        else:
            i += 1

    # update formula with current assignment's
    formula = update_formula(formula, assignment)
    if formula == True: 
        # if the formula has been simplfied to True, then return the assignment that got it there
        return assignment
    elif formula == False:
        # if the formula has been simplified to False, then return None since no assignment exists that can make it True
        return None

    # grab the first variable in the formula
    variable = formula[0][0][0]
    # try assigning it to be True
    option_1 = { key:value for (key,value) in assignment.items() }
    option_1[variable] = True
    # see if there is a set of assignments for option_1
    search_1 = satisfying_assignment(formula, option_1)
    if search_1:
        return search_1

    # try assigning it to be False
    option_2 = { key:value for (key,value) in assignment.items() }
    option_2[variable] = False
    # see if there is a set of assignments for option_2
    search_2 = satisfying_assignment(formula, option_2)
    if search_2:
        return search_2
    


def get_cnf_for_rule_1(student_preferences):
    """
    Takes in the student's preferences dictionary
    Returns a CNF formula expressing the constraint that students are only assigned to rooms in their preferences
    # >>> get_cnf_for_rule_1({'Alice': {'basement', 'penthouse'}, 'Bob': {'kitchen'}, 'Charles': {'basement', 'kitchen'}, 'Dana': {'kitchen', 'penthouse', 'basement'}})
    # [[('Alice_basement', True), ('Alice_penthouse', True)], [('Bob_kitchen', True)], [('Charles_kitchen', True), ('Charles_basement', True)], [('Dana_kitchen', True), ('Dana_basement', True), ('Dana_penthouse', True)]]
    """
    cnf = []
    for student, preferences in student_preferences.items():
        clause = []
        for p in preferences:
            clause.append((student+'_'+p, True))
        cnf.append(clause)
    return cnf

def get_cnf_for_rule_2(student_preferences, room_capacities):
    """
    Takes in the student's preferences dictionary and room capacities dictionary
    Returns a CNF formula expressing the constraint that students are in at most one room
    # >>> get_cnf_for_rule_2({'Alice': {'kitchen', 'penthouse', 'basement'}, 'Bob': {'kitchen', 'penthouse', 'basement'}, 'Charles': {'kitchen', 'penthouse', 'basement'}, 'Dana': {'kitchen', 'penthouse', 'basement'}}, { 'basement': 1, 'kitchen': 2, 'penthouse': 4})
    # [[('Charles_basement', False), ('Charles_kitchen', False)], [('Charles_basement', False), ('Charles_penthouse', False)], [('Charles_kitchen', False), ('Charles_penthouse', False)], [('Alice_basement', False), ('Alice_penthouse', False)], [('Alice_basement', False), ('Alice_kitchen', False)], [('Alice_kitchen', False), ('Alice_penthouse', False)], [('Bob_basement', False), ('Bob_penthouse', False)], [('Bob_basement', False), ('Bob_kitchen', False)], [('Bob_kitchen', False), ('Bob_penthouse', False)], [('Dana_basement', False), ('Dana_penthouse', False)], [('Dana_basement', False), ('Dana_kitchen', False)], [('Dana_kitchen', False), ('Dana_penthouse', False)]]
    """
    cnf = []
    for student, preferences in student_preferences.items():
        pairs = get_groups(list(preferences), 2)
        for p in pairs:
            clause = [(student+'_'+p[0], False), (student+'_'+p[1], False)]
            cnf.append(clause)
    return cnf

def get_groups(values, size):
    """
    Takes in a set of students and an integer size
    Returns an array of tuples with all possible groups of values that are the inputed size
    >>> pairs = get_groups({'basement', 'kitchen', 'penthouse'}, 2)
    >>> len(pairs) == 3
    True
    """
    groups = []
    for v in values:
        # add to previous
        total_groups = len(groups)
        for i in range(total_groups):
            if len(groups[i]) < size:
                groups.append(groups[i] + (v,))
        # start new list
        groups.append((v,))
    # return all groups that match the inputed size
    set_of_groups = []
    for g in groups:
        if len(g) == size:
            set_of_groups.append(g)
    return set_of_groups

def get_students_with_preference(student_preferences, room):
    """
    Takes in student preferences dictionary and a room name
    Returns a set of all students that preference that room
    """
    students = set()
    for student, preferences in student_preferences.items():
        if room in preferences:
            students.add(student)
    return students

def get_cnf_for_rule_3(student_preferences, room_capacities):
    """
    Takes in the student's preferences dictionary and room capacities dictionary
    Returns a CNF formula expressing the constraint of no oversubscribed rooms
    # >>> get_cnf_for_rule_3({'Alice': {'kitchen', 'penthouse', 'basement'}, 'Bob': {'kitchen', 'penthouse', 'basement'}, 'Charles': {'kitchen', 'penthouse', 'basement'}, 'Dana': {'kitchen', 'penthouse', 'basement'}}, { 'basement': 1, 'kitchen': 2, 'penthouse': 4})
    # [[('Alice_kitchen', False), ('Bob_kitchen', False), ('Charles_kitchen', False)], [('Alice_kitchen', False), ('Bob_kitchen', False), ('Dana_kitchen', False)], [('Alice_kitchen', False), ('Dana_kitchen', False), ('Charles_kitchen', False)], [('Dana_kitchen', False), ('Bob_kitchen', False), ('Charles_kitchen', False)], [('Charles_basement', False), ('Alice_basement', False)], [('Alice_basement', False), ('Dana_basement', False)], [('Alice_basement', False), ('Bob_basement', False)], [('Bob_basement', False), ('Charles_basement', False)], [('Bob_basement', False), ('Dana_basement', False)], [('Charles_basement', False), ('Dana_basement', False)]]
    """
    cnf = []
    for room, capacity in room_capacities.items():
        possible_students = get_students_with_preference(student_preferences, room)
        possible_groups = get_groups(possible_students, capacity+1)
        for group in possible_groups:
            clause = [(student+'_'+room, False) for student in group]
            cnf.append(clause)
    return cnf


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rule_1_cnf = get_cnf_for_rule_1(student_preferences)
    rule_2_cnf = get_cnf_for_rule_2(student_preferences, room_capacities)
    rule_3_cnf = get_cnf_for_rule_3(student_preferences, room_capacities)

    return rule_1_cnf + rule_2_cnf + rule_3_cnf


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)

    doctest.run_docstring_examples(satisfying_assignment, globals(), optionflags=_doctest_flags, verbose=False)