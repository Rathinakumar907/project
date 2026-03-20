    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "university_id": current_user.university_id,
        "total_marks": total,
        "attempted_problems": attempted,
        "selected_subjects": [{"id": s.id, "subject_name": s.subject_name} for s in current_user.selected_subjects],
    }
