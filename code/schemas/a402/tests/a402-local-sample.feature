Feature: A402 implementation-artifact local safety baseline
  The non-payable local sample demonstrates ACT 2.1 invariants and artifact checks without
  claiming ACT conformance or simulating payment success.

  @A402-TEST-002
  Scenario: A protected resource without proof returns a payment challenge
    Given the non-payable local sample is running
    When a client requests the protected resource without Payment-Proof
    Then the response status is 402
    And the response contains Payment-Needed

  @A402-TEST-003
  Scenario: Supplying an unvalidated proof does not release the resource
    Given the non-payable local sample is running
    When a client retries the protected resource with an arbitrary Payment-Proof
    Then the response status is 402
    And resource_delivered is false
