import { Component } from 'react';
import './app.scss';

class App extends Component {
  componentDidMount() {
    // 应用启动时检查登录状态
  }

  componentDidShow() {}

  componentDidHide() {}

  render() {
    return this.props.children;
  }
}

export default App;