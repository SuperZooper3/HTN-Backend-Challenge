from flask import Blueprint, request
from .. import get_skills_cache
from ..services.skills_service import *

skills_bp = Blueprint('skills_bp', __name__)


@skills_bp.route('/skills', methods=['GET'])
def skills():
    output = {}
    min_frequency = request.args.get("min_frequency", None, type=int)
    max_frequency = request.args.get("max_frequency", None, type=int)
    min_average_rating = request.args.get("min_average_rating", None, type=float)
    max_average_rating = request.args.get("max_average_rating", None, type=float)
    keyword = request.args.get("keyword", None, type=str)

    skills_cache = get_skills_cache()

    for skill in skills_cache:
        if check_skill_frequency(skill, min_frequency, max_frequency) and check_skill_average_rating(skill, min_average_rating, max_average_rating) and (keyword is None or keyword.lower() in skill.lower()):
            output[skill] = {
                "frequency": skills_cache[skill]["frequency"],
                "average_rating": round(skills_cache[skill]["total_rating"] / skills_cache[skill]["frequency"], 2)
            }
    return output