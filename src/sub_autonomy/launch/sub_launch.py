import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='sub_autonomy',
            executable='sub_controller',
            name='sub_controller'
        ),
        launch_ros.actions.Node(
            package='sub_autonomy',
            executable='mission_executor',
            name='mission_executer'
        )
    ])
