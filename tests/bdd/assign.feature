Feature: Managing team lane assignments
  As a Discord user or moderator
  I want to assign and remove team members from lanes
  So that team organization is maintained

  Background:
    Given the team lane system is initialized
    And all lanes are empty

  Scenario: User assigns themselves to a specific available lane
    Given team 2 lane 5 is empty
    When the user "user1" runs "assign --team 2 --lane 5"
    Then "user1" should be assigned to team 2 lane 5
    And the system should respond with "Successfully assigned user1 to Team 2, Lane 5."

  Scenario: User tries to assign themselves to an occupied lane
    Given "user1" is assigned to team 1 lane 3
    When the user "user2" runs "assign --team 1 --lane 3"
    Then "user2" should not be assigned to team 1 lane 3
    And the system should respond with a message containing "Lane taken"
    And the system should suggest alternative lanes

  Scenario: User assigns themselves to any empty lane
    Given there are available lanes
    When the user "user1" runs "assign --any-empty"
    Then "user1" should be assigned to a lane
    And the system should respond with a success message

  Scenario: Admin assigns a member to a specific lane
    Given "alice" is not assigned
    When the admin runs "assign --member alice --team 1 --lane 3"
    Then "alice" is assigned to team 1 lane 3
    And the system should respond with "Successfully assigned alice to Team 1, Lane 3."

  Scenario: Admin assigns a member to a random lane
    Given there are available lanes
    When the admin runs "assign --member bob --random"
    Then "bob" should be assigned to a lane
    And the system should respond with a success message

  Scenario: Admin removes a member
    Given "carol" is assigned to team 3 lane 4
    When the admin runs "remove --member carol"
    Then "carol" is no longer assigned to any lane
    And the system should respond with a message containing "Removed carol from"

  Scenario: User tries to assign to a non-existent team
    When the user "user1" runs "assign --team 10 --lane 5"
    Then the system should respond with a message containing "Team 10 does not exist"

  Scenario: User tries to assign to a non-existent lane
    When the user "user1" runs "assign --team 2 --lane 15"
    Then the system should respond with a message containing "Lane 15 does not exist"

  Scenario: Admin tries to remove a non-assigned member
    When the admin runs "remove --member nonexistent"
    Then the system should respond with a message containing "not assigned to any lanes"

  Scenario: All lanes are occupied
    Given all lanes are occupied
    When the user "newuser" runs "assign --any-empty"
    Then the system should respond with a message containing "No empty lanes available"

Scenario: User lists all team assignments
    Given "alice" is assigned to team 1 lane 3
    And "bob" is assigned to team 2 lane 5
    When the user "user1" runs "list"
    Then the system should respond with a message containing "Current Team Assignments"
    And the system should respond with a message containing "Team 1"
    And the system should respond with a message containing "Lane 3: alice"
    And the system should respond with a message containing "Team 2"
    And the system should respond with a message containing "Lane 5: bob"
