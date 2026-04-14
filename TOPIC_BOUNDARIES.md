# Pauline Topics — Boundary Notes

Use this file as a practical guardrail when adjacent topics begin to collapse into one another.

## Core Principle

Adjacent topics may cite some of the same Pauline passages, but each module should keep a distinct center of gravity:

- one primary question the module answers
- one dominant angle of explanation
- one main result it highlights

If a topic begins to reteach its neighbor instead of supporting it, tighten the scope.

## PT-01 Justification by Faith

Primary question:
How is a sinner declared righteous before God?

Center of gravity:
- the verdict of being declared righteous
- not by works of the Law
- through faith in Christ

Emphasize:
- justified
- verdict
- declared righteous
- works versus faith
- acceptance before God

Avoid drifting into:
- a broad study of faith itself
- a broad study of righteousness as a theme

## PT-03 Faith

Primary question:
What is the human response by which God’s promise is received and the Christian life is lived?

Center of gravity:
- trust in God and in Christ
- faith contrasted with works
- believing God’s promise
- continuing to live by faith

Emphasize:
- trust
- believing
- promise
- reliance
- living by faith

Avoid drifting into:
- the legal verdict of justification
- the broader category of righteousness as a gift or attribute

## PT-05 Righteousness

Primary question:
What is the righteousness God reveals and gives?

Center of gravity:
- God’s righteousness
- right standing before God
- not self-established righteousness
- righteousness given on the basis of faith

Emphasize:
- God’s righteousness
- gift of righteousness
- right standing
- revealed righteousness
- credited righteousness

Avoid drifting into:
- making justification the whole topic
- making faith the whole topic

## PT-06 Redemption

Primary question:
What deliverance has Christ secured for His people?

Center of gravity:
- release from bondage
- rescue from dominion
- transfer into Christ’s kingdom
- present redemption with future completion

Emphasize:
- rescue
- deliverance
- release
- liberation
- day of redemption

Avoid drifting into:
- making forgiveness the whole topic
- reducing redemption to one synonym for pardon

## PT-18 Forgiveness

Primary question:
How does God deal with guilt and trespass in Christ?

Center of gravity:
- pardon of sins
- trespasses no longer counted
- forgiveness received from God
- forgiveness extended to others

Emphasize:
- pardon
- forgiveness
- trespasses
- no longer counted
- forgive as the Lord forgave you

Avoid drifting into:
- making redemption the whole topic
- focusing mainly on bondage and deliverance language

## PT-07 Reconciliation

Primary question:
How are enemies brought back into restored relationship with God?

Center of gravity:
- alienation removed
- hostility ended
- relationship restored
- reconciliation accomplished by Christ

Emphasize:
- enemies
- alienation
- restored relationship
- be reconciled to God
- ministry/message of reconciliation

Avoid drifting into:
- making peace merely an inner feeling or outcome term
- making the topic only about access or assurance

## PT-19 Peace with God

Primary question:
What settled peace do believers now have before God?

Center of gravity:
- peace as the result of justification
- hostility ended
- settled standing before God
- rejoicing and nearness

Emphasize:
- peace with God
- settled peace
- standing in grace
- rejoicing in God
- no longer at enmity

Avoid drifting into:
- reteaching reconciliation as the main topic
- shifting into access-to-God as the main focus

## PT-20 Access to God

Primary question:
What open approach to the Father do believers now have through Christ?

Center of gravity:
- access to the Father
- nearness
- boldness and confidence
- one Spirit through Christ

Emphasize:
- access
- approach
- boldness
- confidence
- brought near

Avoid drifting into:
- making peace with God the main point
- making reconciliation the main point

## PT-12 Union with Christ

Primary question:
What does it mean for believers to be joined to Christ Himself?

Center of gravity:
- being in Christ
- participation in His death and resurrection
- shared life with Him
- identity derived from union with Him

Emphasize:
- union
- in Christ
- with Christ
- joined to His death and resurrection
- shared life

Avoid drifting into:
- making transformed behavior the whole topic
- collapsing into new creation language alone

## PT-13 New Creation

Primary question:
What new reality has God brought about in those who are in Christ?

Center of gravity:
- the old has passed away
- the new has come
- new self
- transformed pattern of life

Emphasize:
- new creation
- old and new
- new self
- renewal
- transformed life

Avoid drifting into:
- making participation/union the whole topic
- relying mostly on death-and-resurrection union language

## Working Rule For Shared Texts

Shared texts are acceptable when the angle clearly differs.

Examples:
- `Romans 3:21–22`
  - `PT-01`: supports the verdict of justification
  - `PT-05`: supports the revelation and gift of righteousness
- `Romans 4:3`
  - `PT-01`: Abraham as an example of justification by faith
  - `PT-03`: Abraham as an example of trusting God
  - `PT-05`: Abraham as an example of righteousness credited
- `Romans 5:1`
  - `PT-01`: result of justification
  - `PT-03`: result connected to faith
  - `PT-19`: central defining text for peace with God
- `Ephesians 1:7`
  - `PT-06`: redemption language may support deliverance, but should not dominate the whole module with pardon language
  - `PT-18`: central support for forgiveness through Christ’s blood
- `Colossians 1:13–14`
  - `PT-06`: emphasize rescue from dominion and transfer into the Son’s kingdom
  - `PT-18`: emphasize forgiveness of sins
- `Romans 5:10–11`
  - `PT-07`: central support for reconciliation
  - `PT-19`: supporting background for the peace that results
- `Romans 5:2`
  - `PT-19`: peace enjoyed in a standing of grace
  - `PT-20`: central support for access to God
- `Romans 6:3–5`
  - `PT-12`: central union-with-Christ text
  - `PT-13`: use sparingly, and only when the emphasis is newness of life rather than union itself

## Editing Checklist

Before finalizing a topic, ask:

1. What exact question is this module answering?
2. If I removed the title, would the summary still clearly point to this topic and not its neighbor?
3. Does the definition avoid self-reference or circular wording?
4. Does the definition avoid depending on another topic title for its main meaning?
5. If another topic is mentioned in the definition, is the center of gravity still clearly this topic?
6. Are the definition, summary, and key verse all pulling in the same direction?
7. Is the module using shared texts with a distinct angle, or just repeating another topic?
8. Does the summary restate this topic’s main point before moving to causes, results, or neighboring themes?
9. Does the module still look distinct after checking summary drift and overlap against other modules?
10. Are the observation, reflection, and application questions distinct, text-based, and free from speculation?

Use `python3 scripts/validate_module_set.py modules --bsb-json bsb_usj` as the preferred post-draft check, or run `python3 scripts/check_definitions.py`, `python3 scripts/check_summaries.py`, `python3 scripts/check_questions.py`, and `python3 scripts/check_topic_overlap.py` individually when needed.
