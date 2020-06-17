#!/usr/bin/env python
#coding=utf-8

# 软件许可协议 (BSD License)
#
# 版权所有 Jim-Office
# 保留所有权利。
#
# 这份授权条款，在使用者符合以下三条件的情形下，授予使用者使用及再散播本软件
# 包装原始码及二进位可执行形式的权利，无论此包装是否经改作皆然：
#  
#  * 对于本软件源代码的再散播，必须保留上述的版权宣告、此三条件表列，以及下
#    述的免责声明。
#  * 对于本套件二进位可执行形式的再散播，必须连带以文件以及/或者其他附于散播
#    包装中的媒介方式，重制上述之版权宣告、此三条件表列，以及下述的免责声明。
#  * 未获事前取得书面许可，不得使用 SRI INternational 或本软件贡献者之名称，
#    来为本软件之衍生物做任何表示支持、认可或推广、促销之行为。
#
# 本软件由版权所有者及其贡献者按照原样提供。任何明示或暗示的保证，包括但不限于对
# 适销性和适用于特定用途的暗示保证都不作承诺。在任何情况下，版权所有人及其贡献者
# 均不对任何直接、间接、附带、特殊、惩戒性或后果性损失（包括但不限于）
#
# 本软件是由版权所有者及本软件之贡献者以现状（"as is"）提供， 本软件包装
# 不负任何明示或默示之担保责任，包括但不限于就适售性以及特定目的的适用性为默示
# 性担保。版权所有者及本软件之贡献者，无论任何条件、 无论成因或任何责任主义、
# 无论此责任为因合约关系、无过失责任主义或因非违约之侵权（包括过失或其他原因等）
# 而起，对于任何因使用本软件包装所产生的 任何直接性、间接性、偶发性、特殊性、
# 惩罚性或任何结果的损害（包括但不限于替代商品或劳务之购用、使用损失、资料损失、
# 利益损失、业务中断等等），不负任何责任，即在该种使用已获事前告知可能会造成此类
# 损害的情形下亦然。
#
# 作者: Jim CHAN
# 邮箱：522706601@qq.com

import sys
import copy
import rospy
import numpy as np
import math
import moveit_commander
import moveit_msgs.msg
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Float64
from std_msgs.msg import String
from sensor_msgs.msg import Imu


class PigotController(object):
  def __init__(self):

    super(PigotController, self).__init__()

    rospy.init_node('pigot_controller_node',
                    anonymous=True)
    self.joint1_pos_pub = rospy.Publisher('/pigot/joint1_position_controller/command', Float64, queue_size=10)
    self.joint2_pos_pub = rospy.Publisher('/pigot/joint2_position_controller/command', Float64, queue_size=10)
    self.joint3_pos_pub = rospy.Publisher('/pigot/joint3_position_controller/command', Float64, queue_size=10)
    self.joint4_pos_pub = rospy.Publisher('/pigot/joint4_position_controller/command', Float64, queue_size=10)
    self.joint5_pos_pub = rospy.Publisher('/pigot/joint5_position_controller/command', Float64, queue_size=10)
    self.joint6_pos_pub = rospy.Publisher('/pigot/joint6_position_controller/command', Float64, queue_size=10)
    self.joint7_pos_pub = rospy.Publisher('/pigot/joint7_position_controller/command', Float64, queue_size=10)
    self.joint8_pos_pub = rospy.Publisher('/pigot/joint8_position_controller/command', Float64, queue_size=10)
    self.joint9_pos_pub = rospy.Publisher('/pigot/joint9_position_controller/command', Float64, queue_size=10)
    self.joint10_pos_pub = rospy.Publisher('/pigot/joint10_position_controller/command', Float64, queue_size=10)
    self.joint11_pos_pub = rospy.Publisher('/pigot/joint11_position_controller/command', Float64, queue_size=10)
    self.joint12_pos_pub = rospy.Publisher('/pigot/joint12_position_controller/command', Float64, queue_size=10)
    

    moveit_commander.roscpp_initialize(sys.argv)

    self.robot = moveit_commander.RobotCommander()

    self.scene = moveit_commander.PlanningSceneInterface()

    group_name = "arm"
    self.group = moveit_commander.MoveGroupCommander(group_name)

    self.display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',
                                                   moveit_msgs.msg.DisplayTrajectory,
                                                   queue_size=20)

    self.planning_frame = self.group.get_planning_frame()

    self.eef_link = self.group.get_end_effector_link()

    self.group_names = self.robot.get_group_names()
    

    self.step_num = 40 
    self.rate = 2 
    self.l1 = 0.15 
    self.l2 = 0.35 
    self.l3 = 0.35 
    self.center_correct = 0.075 
    self.v_linear = 0.0
    self.v_angular = 0.0
    self.state = 'keep'
    self.orientation = np.array([0.0, 0.0, 0.0])
    

    joint_goal = np.array([0, -math.pi/4, math.pi/4, 0, 0, 0])
    self.go_to_joint_state(joint_goal)
    print('初始化成功')
    return
     
  def model_setup(self):

    print("选择机器人的控制模式，'t'为键盘控制，'a'为自动导航")
    model_type = raw_input()
    return model_type
    
  def gait_plan(self, v_linear, v_angular):

    gait_data = np.zeros((self.step_num, 12))
    data = self.trajectory_data(v_linear, v_angular)
    x_line = data[0, :]
    y_line = data[1, :]
    z_line = data[2, :]
    for t in range(gait_data.shape[0]):
        if (t < 20):
            xf = x_line[t]
            xb = x_line[t + 20]
            yf = y_line[t]
            yb = y_line[t + 20]
            zf = z_line[t]
            zb = z_line[t + 20]
        else:
            xf = x_line[t]
            xb = x_line[t - 20]
            yf = y_line[t]
            yb = y_line[t - 20]
            zf = z_line[t]
            zb = z_line[t - 20]
        gait_data[t, 0], gait_data[t, 1 ], gait_data[t, 2 ] = self.leg_ikine(xf, yf + 0.15, zf)
        gait_data[t, 3], gait_data[t, 4 ], gait_data[t, 5 ] = self.leg_ikine(xb, -yb + 0.15, zb)
        gait_data[t, 6], gait_data[t, 7 ], gait_data[t, 8 ] = self.leg_ikine(xb, -yb + 0.15, zb)
        gait_data[t, 9], gait_data[t, 10], gait_data[t, 11] = self.leg_ikine(xf, yf + 0.15, zf)
    return gait_data
    
  def cartesian_path_plan(self, point_array):


    n = point_array.shape[0]
    print(n)
    waypoints = []
    wpose = self.group.get_current_pose().pose
    for i in range(n):
      wpose.position.x += point_array[i, 0]
      wpose.position.y += point_array[i, 1]
      wpose.position.z += point_array[i, 2]
      waypoints.append(copy.deepcopy(wpose))



    (plan, fraction) = self.group.compute_cartesian_path(
                                       waypoints,   
                                       0.01,        
                                       0.0)         
    return plan, fraction
    
  def go_to_joint_state(self, joint_goal):

    joint_state = self.group.get_current_joint_values()
    joint_state[0] = joint_goal[0]
    joint_state[1] = joint_goal[1]
    joint_state[2] = joint_goal[2]
    joint_state[3] = joint_goal[3]
    joint_state[4] = joint_goal[4]
    joint_state[5] = joint_goal[5]

    self.group.go(joint_state, wait=True)


    self.group.stop()
    return
    
  def leg_ikine(self, x, y, z):

    theta1 = math.atan2(y, x) + math.atan2(self.l1, -(x**2 + y**2 - self.l1**2)**0.5)
    c1 = math.cos(theta1)    
    s1 = math.sin(theta1) 
    c3 = (x**2 + y**2 + z**2 - self.l1**2 - self.l2**2 - self.l3**2) / (2 * self.l2 * self.l3)
    s3 = (1 - c3**2)**0.5
    theta3 = math.atan2(s3, c3)
    s2p = (self.l3 * s3) / ((y * s1 + x * c1)**2 + z**2)**0.5
    c2p = (1 - s2p**2)**0.5
    theta2p = -math.atan2(s2p, c2p)
    thetap = -math.atan2(z, -(y * s1 + x * c1))
    theta2 = theta2p - thetap
    theta1 = theta1 - math.pi
    return theta1, theta2, theta3
  
  def trajectory_data(self, v_linear, v_angular):
    v_E1 = v_linear 
    v_E2 = v_angular 

    x, y, z = np.zeros(self.step_num / 2), np.zeros(self.step_num / 2), np.zeros(self.step_num / 2)
    E_long = v_E1 
    E_lateral = v_E2 
    h = 0.1 
    theta = np.linspace(0, 2 * math.pi, self.step_num / 2)
    for i in range(self.step_num / 2):
      x[i] = h * (1 - math.cos(theta[i])) / 2
      y[i] = E_lateral * (theta[i] - math.sin(theta[i])) / (2 * math.pi)
      z[i] = E_long * (theta[i] - math.sin(theta[i])) / (2 * math.pi)

    x = - x + 0.6
    y = y - E_lateral
    z = z - E_long * 2.0 / 4 + self.center_correct

    x_gait = np.hstack((x[10 : 20], x[0 : 20]**0 * x[19], x[0 : 10]))
    y_gait = np.hstack((y[10 : 20], np.linspace(y[19], y[0], self.step_num / 2), y[0 : 10]))
    z_gait = np.hstack((z[10 : 20], np.linspace(z[19], z[0], self.step_num / 2), z[0 : 10]))
    forward_gait = np.vstack((x_gait, y_gait, z_gait))
    return forward_gait
    
  def teleop_control(self):

    rospy.Subscriber('/pigot/action_chatter', String, self.body_action_cb)
    rospy.Subscriber("/imu", Imu, self.orientation_cb, queue_size = 1)
    while(1):
      if self.state == 'walk':
        gait_data = self.gait_plan(self.v_linear, self.v_angular)
        self.body_action_pub(gait_data)
      elif self.state == 'keep':
        gait_data = self.gait_plan(0, 0)
        self.body_action_pub(gait_data)
      elif self.state == 'overturn':
        self.stand_up()
      print(self.state)
    rospy.spin()
    
  def body_action_cb(self, action_msgs):

    self.state = 'walk'
    if (action_msgs.data == 'w'):
      self.v_linear = 0.1
      self.v_angular = 0.0
    elif (action_msgs.data == 's'):
      self.v_linear = -0.1
      self.v_angular = 0.0
    elif (action_msgs.data == 'a'):
      self.v_linear = 0.0
      self.v_angular = 0.05
    elif (action_msgs.data == 'd'):
      self.v_linear = 0.0
      self.v_angular = -0.05
    elif (action_msgs.data == 'k'):
      self.state = 'keep'
      self.v_linear = 0.0
      self.v_angular = 0.0
    return
  
  def orientation_cb(self, imu_msgs):

    x = imu_msgs.orientation.x
    y = imu_msgs.orientation.y
    z = imu_msgs.orientation.z
    w = imu_msgs.orientation.w


    w_x = imu_msgs.angular_velocity.x
    w_y = imu_msgs.angular_velocity.y
    w_z = imu_msgs.angular_velocity.z


    a_x = imu_msgs.linear_acceleration.x
    a_y = imu_msgs.linear_acceleration.y
    a_z = imu_msgs.linear_acceleration.z


    r = math.atan2(2 * (w * x + y * z), 1 - 2 * (x**2 + y**2))
    p = math.asin(2 * (w * y - z * x))
    y = math.atan2(2 * (w * z + x * y), 1 - 2 * (y**2 + z**2))
    self.orientation[0] = r
    self.orientation[1] = p
    self.orientation[2] = y


    if ((abs(r) > 0.8) and (abs(r) < 2.8)) or ((abs(p) > 0.8) and (abs(p) < 2.8)):
      self.state = 'overturn'
    print(self.orientation)     
    return
  
  def body_action_pub(self, gait_np_data):

    data_length = gait_np_data.shape[0]
    pause = rospy.Rate(data_length * self.rate)
    gait_data = Float32MultiArray()
    gait_data.data = gait_np_data
    j = 0
    while (j<1):
      for i in range(data_length):
        self.joint1_pos_pub.publish(gait_data.data[i, 0])
        self.joint2_pos_pub.publish(gait_data.data[i, 1])
        self.joint3_pos_pub.publish(gait_data.data[i, 2])
        self.joint4_pos_pub.publish(gait_data.data[i, 3])
        self.joint5_pos_pub.publish(gait_data.data[i, 4])
        self.joint6_pos_pub.publish(gait_data.data[i, 5])
        self.joint7_pos_pub.publish(gait_data.data[i, 6])
        self.joint8_pos_pub.publish(gait_data.data[i, 7])
        self.joint9_pos_pub.publish(gait_data.data[i, 8])
        self.joint10_pos_pub.publish(gait_data.data[i, 9])
        self.joint11_pos_pub.publish(gait_data.data[i, 10])
        self.joint12_pos_pub.publish(gait_data.data[i, 11])
        pause.sleep()
      j = j + 1
    return
  
  def arm_action_pub(self, plan):

    self.group.execute(plan, wait=True)
    return
    
    
  def stand_up(self):

    gait_data = np.zeros((self.step_num, 12))
    gait_data[:, 0], gait_data[:, 1 ], gait_data[:, 2 ] = self.leg_ikine(0.2, 0.15, self.center_correct)
    gait_data[:, 3], gait_data[:, 4 ], gait_data[:, 5 ] = self.leg_ikine(0.2, 0.15, self.center_correct)
    gait_data[:, 6], gait_data[:, 7 ], gait_data[:, 8 ] = self.leg_ikine(0.2, 0.15, self.center_correct)
    gait_data[:, 9], gait_data[:, 10], gait_data[:, 11] = self.leg_ikine(0.2, 0.15, self.center_correct)
    self.body_action_pub(gait_data)
    pause = rospy.Rate(2)
    pause.sleep()

    if (self.orientation[1] > 0.8) and (self.orientation[1] < 2.8):
      joint_goal = np.array([math.pi/2, -math.pi/4, math.pi/4, 0, 0, 0])
      self.go_to_joint_state(joint_goal)
    elif (self.orientation[0] > 0.8) and (self.orientation[0] < 2.8):
      joint_goal = np.array([0, -math.pi/4, math.pi/4, 0, 0, 0])
      self.go_to_joint_state(joint_goal)
    elif (self.orientation[1] < -0.8) and (self.orientation[1] > -2.8):
      joint_goal = np.array([-math.pi/2, -math.pi/4, math.pi/4, 0, 0, 0])
      self.go_to_joint_state(joint_goal)
    elif (self.orientation[0] < -0.8) and (self.orientation[0] > -2.8):
      joint_goal = np.array([3.14, -math.pi/4, math.pi/4, 0, 0, 0])
      self.go_to_joint_state(joint_goal)

    joint_state = self.group.get_current_joint_values()
    joint_goal = np.array([joint_state[0], math.pi/3, 0, 0, 0, 0])
    self.go_to_joint_state(joint_goal)
    joint_goal = np.array([0, -math.pi/4, math.pi/4, 0, 0, 0])
    self.go_to_joint_state(joint_goal)
    

    for i in range(self.step_num):
      gait_data[i, 0], gait_data[i, 1 ], gait_data[i, 2 ] = self.leg_ikine(0.2 + 0.4 * i / self.step_num, 0.15, self.center_correct)
      gait_data[i, 3], gait_data[i, 4 ], gait_data[i, 5 ] = self.leg_ikine(0.2 + 0.4 * i / self.step_num, 0.15, self.center_correct)
      gait_data[i, 6], gait_data[i, 7 ], gait_data[i, 8 ] = self.leg_ikine(0.2 + 0.4 * i / self.step_num, 0.15, self.center_correct)
      gait_data[i, 9], gait_data[i, 10], gait_data[i, 11] = self.leg_ikine(0.2 + 0.4 * i / self.step_num, 0.15, self.center_correct)
    self.body_action_pub(gait_data)
    self.state = 'keep'
        
    return
    
    
def main():
  try:
      pc = PigotController()

      model_type = pc.model_setup()
      while not rospy.is_shutdown():

        if model_type == 't':
          pc.teleop_control()
        elif model_type == 'a':
          pc.auto_navigation()
  except rospy.ROSInterruptException:
      pass



if __name__ == '__main__':
  main()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
