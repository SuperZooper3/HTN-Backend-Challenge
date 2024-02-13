from .. import get_skills_cache

# Helper methods for checks
def check_skill_frequency(skill, min_frequency, max_frequency):
    frequency = get_skills_cache()[skill]["frequency"]
    return (min_frequency is None or frequency >= min_frequency) and (max_frequency is None or frequency <= max_frequency)

def check_skill_average_rating(skill, min_average_rating, max_average_rating):
    skills_cache = get_skills_cache()
    average_rating = skills_cache[skill]["total_rating"] / skills_cache[skill]["frequency"]
    return (min_average_rating is None or average_rating >= min_average_rating) and (max_average_rating is None or average_rating <= max_average_rating)
