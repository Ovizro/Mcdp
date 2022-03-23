from entities import McdpStack()


mcdp_stack_id = global_var(dp_score, STACK_ID_SC, 0)


@lib_func()
def enter_stack() -> None:
    global mcdp_stack_id
    cdef:
        Selector top
        selector lower

    top = Selector("@e", tag={get_tag(), "stack_top"}, limit=1)
    lower = Selector("@e", tag={get_tag(), "lower_stack"}, limit=1)
    
    lower.remove_tag("lower_stack")
    top.add_tag("lower_stack")
    top.remove_tag("stack_top")

    stack = McdpStack()
    mcdp_stack_id += 1
    

@lib_func()
def leave_stack() -> None:
    global mcdp_stack_id

    top = Selector("@e", tag={get_tag(), "stack_top"}, limit=1)
    lower = Selector("@e", tag={get_tag(), "lower_stack"}, limit=1)

    top.remove()
    lower.add_tag("stack_top")
    lower.remove_tag("lower_stack")

    mcdp_stack_id -= 2
    s = dp_score(STACK_ID_SC, selector=selector(McdpStack))
    with s == mcdp_stack_id:
        Selector("@s").add_tag("lower_stack")
    mcdp_stack_id += 1