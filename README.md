[![Coverage Status](https://coveralls.io/repos/Skill-Match/skill-match-api/badge.svg?branch=master&service=github)](https://coveralls.io/github/Skill-Match/skill-match-api?branch=master)
[![Build Status](https://travis-ci.org/Skill-Match/skill-match-api.svg?branch=master)](https://travis-ci.org/Skill-Match/skill-match-api)

## Skill-Match-API

skill-match-api is an API to feed JSON data of Parks and Recreation Centers in the Las Vegas area. Park data and location is stored in a PostGIS database so it can be used to query which parks are closest to you.

It is designed to be used by a front-end team of developers to create web applications for local municipalities.

A description of the endpoints is coming soon. For now you can see the endpoints and some of the HTTP Methods (GET, POST, PUT, DELETE) at the following link. It may take up to 30 seconds to load, as it is a free Heroku app.

http://skill-match.herokuapp.com/docs/

## Features of the application as a whole:

- Search for parks in your area using name or location. Icons make it easy to see what sports are available at each park.

- Search for Matches in your area. Find a match with a relative skill level, so you can find the perfect match for you.

- Show distance to each park or match using geolocation or zip-code

- Filter search results by sport, or coming soon, skill level.

- Create a meet-up yourself. You can schedule a Tennis, Basketball, Football, Soccer, ^Pickleball, or Other match.

- Profile page for each user shows their Skill (per sport) and Sportsmanship levels on a 1-100 scale.

- Feedback is provided using a simple 3-slider bars: rating their opponents Skill, Sportsmanship, and Crowd Level. Crowd Level is a slider ranking(1-5) how crowded the court was.

- Feedback is anonymous by updating skills only after every 3 feedbacks.

- Player Skills are based off a simple algorithm which weights feedback based on the reviewer's skill, sportsmanship and experience.


^Pickleball is a game similar to Tennis, played with a ball similar to a heavy wiffle ball. We are looking to build something specific for Henderson, NV.
