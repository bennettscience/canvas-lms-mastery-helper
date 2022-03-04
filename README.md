# Canvas Learning Mastery Helper

This is an upgrade to the
[old learning mastery helper](https://github.com/bennettscience/canvas-learning-mastery),
adding a better UI, better data handling, faster loads and updates, and more
options for users to explore and play with data from Canvas.

## Canvas LMS and Learning Outcomes

Canvas provides a method for instructors to attach learning outcomes to
assignments and assessments. The rubric mechanism works well, but Canvas lacks
powerful tools for evaluating and using that data to make instructional
decisions. The Learning Mastery Gradebook provides a high-level overveiew of
student performance on assessed outcomes, but seeing individual results and
trends is much more difficult.

If you switch to the Individual View in the gradebook, you can click a student
name and then use the Learning Mastery tab to see all aligned Outcomes and their
scores. This view gets closer to being helpful because it shows scores on
assessments over time, which allows you to track progress (growth vs decline) in
a chart. To see reports organized by Outcome, you can go to Outcomes and then
click on the title of the individual item. This shows the assignments it was
assessed on and a list of students who were assessed. This list is not sortable
and can be many, many pages long.

There is a lack of consistency in how Outcomes are presented, which amkes them
less compelling to use.

## Learning Mastery Helper

The Learning Mastery Helper runs as a standalone web application which can
ingest data from Canvas and help instructors and students make informed
instructional decisions. There are several benefits provided by using this tool:

1. Outcomes, outcome attempts, and assignments can be imported, linked, and
   explored independently.
2. Outcome results can be linked to assignment scores for automatic scoring in
   the traditional gradebook.
3. Users are authorized via the Canvas OAuth sign in flow, meaning the access
   they have in Canvas carries over automatically into the Helper interface.
4. Canvas' scoring options on Outcomes have significant limitations. Instructors
   can choose one of several custom scoring options to better undersand student
   performance on Outcomes over time.

## Installation

Instructions for deploying on a Linux VPS are on INSTALL.md.
