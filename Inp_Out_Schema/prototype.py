def receive_ball_data(data: list[dict[str, float]]) -> None:
    """
    Interface Function
    This function is basically 
    Called by previous module to pass output  
    Stores or processes internally.
    """
    pass
#Note: We may remove receive_ball_data interface function and replace it with internal function, that would instead call
#the previous module function to get the tracked data. In this case, the internal function will provide us with the
#tracked list Example below
def get_ball_data() -> list[dict[str, float]]:
    """
    Not an interface function but replacement to above interface function. 
    """
    pass


def get_trajectory_analysis() -> list[Dict[str, object]], dict[str, object], dict[str, object], string:
    """
    Interface Function
    
    Called by next module to get the processed trajectory prediction.
    
    Returns:
        Dict: Contains predicted_path list, impact_location, bounce_point, swing_type
    """
    pass
