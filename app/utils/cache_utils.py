from ..models.models import Skills
from .. import skills_cache

# Generate a fresh cache of the skills' frequency and total rating
def generate_skills_cache():
    fresh_cache = {}
    all_skills = Skills.query.all()
    for skill in all_skills:
        if skill.name not in fresh_cache:
            fresh_cache[skill.name] = {
                "frequency": 0,
                "total_rating": 0
            }
        fresh_cache[skill.name]["frequency"] += 1
        fresh_cache[skill.name]["total_rating"] += skill.rating

    return fresh_cache

# Logic for updating the skills cache when a new skill is added for a participant
def new_participant_skill_to_cache(skill, rating):
    """Updates the skills cache with a new skill, or updates the frequency and total rating of an existing skill. For when it's a participant's first time adding a skill. Not for when they update their rating."""
    if skill not in skills_cache:
        skills_cache[skill] = {
            "frequency": 1,
            "total_rating": rating
        }
    else:
        skills_cache[skill]["frequency"] += 1
        skills_cache[skill]["total_rating"] += rating
