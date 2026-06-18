def check_quota(user, page_count) -> tuple[bool, str]:
    quota = user.get_quota()
    if user.pages_used_this_month + page_count > quota:
        return (False, "Not enough qouta left")
    else:
        return (True, "")