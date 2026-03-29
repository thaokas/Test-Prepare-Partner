export default defineAppConfig({
  pages: [
    'pages/home/index',
    'pages/login/index',
    'pages/register/index',
    'pages/plan/index',
    'pages/plan/create/index',
    'pages/plan/detail/index',
    'pages/task/index',
    'pages/checkin/index',
    'pages/profile/index',
    'pages/chat/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#4A90D9',
    navigationBarTitleText: '备考搭子',
    navigationBarTextStyle: 'white'
  },
  tabBar: {
    color: '#999999',
    selectedColor: '#4A90D9',
    backgroundColor: '#ffffff',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/home/index',
        text: '首页',
        iconPath: 'assets/icons/home.png',
        selectedIconPath: 'assets/icons/home-active.png'
      },
      {
        pagePath: 'pages/plan/index',
        text: '计划',
        iconPath: 'assets/icons/plan.png',
        selectedIconPath: 'assets/icons/plan-active.png'
      },
      {
        pagePath: 'pages/checkin/index',
        text: '打卡',
        iconPath: 'assets/icons/checkin.png',
        selectedIconPath: 'assets/icons/checkin-active.png'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
        iconPath: 'assets/icons/profile.png',
        selectedIconPath: 'assets/icons/profile-active.png'
      }
    ]
  }
});