def naked(env):
    # naked position: don't buy any stock
    s_T = env.get_attr('s_T')[0] 
    s_X = env.get_attr('s_X')[0] 
    amount = env.get_attr('amount')[0] 
    option_price = env.get_attr('option_price')[0] 
    if s_T > s_X:
        return amount*option_price + amount*(s_X-s_T)
    else:
        return 0


def covered(env):
    s_T = env.get_attr('s_T')[0] 
    s_X = env.get_attr('s_X')[0] 
    s_0 = env.get_attr('s_0')[0] 
    amount = env.get_attr('amount')[0] 
    option_price = env.get_attr('option_price')[0] 
    rate = env.get_attr('rate')[0] 
    T = env.get_attr('T')[0]/365.0 
    if s_T > s_X:
        return amount*option_price*((1+rate)**T) + amount*(s_X-s_0) - amount*s_0*((1+rate)**T-1)
    else:
        return amount*option_price*((1+rate)**T) + amount*(s_T-s_0) - amount*s_0*((1+rate)**T-1)


if __name__ == "__main__":
    pass
