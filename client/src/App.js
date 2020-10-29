import React from 'react';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";
import PicWall from './components/PicWall/PicWall.js';
import HistoryBoard from './components/History/History.js';
import UserUpload from './components/UserUpload/UserUpload.js';
import 'antd/dist/antd.css';
import './App.css'
import {Layout, Menu, Breadcrumb, Typography, Avatar, Dropdown, Modal, Form, Input, message } from 'antd';
import { UserOutlined, LaptopOutlined, NotificationOutlined } from '@ant-design/icons';
import {connect} from 'react-redux';
import axios from 'axios';
import config from './config';

const { Header, Content, Sider, Footer } = Layout;
const {Title} = Typography;

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      userName: "",
      loginModalVisible: false,
      logoutModalVisible: false,
      activatePageKey: "1",
      save: false,
    }
  }

  formRef = React.createRef();

  componentDidMount() {
    const token = localStorage.getItem('token');

    if (token) {
      axios.post(`${config.baseAddress}/autoLogin`, {}, {headers: {
        authorization: "bare " + token
      }}).then(res => {
        if(res.status === config.success){
          const {authData, status} = res.data;

          if(status){
            this.props.login(authData.userName);
            this.setState({userName: authData.userName});
          }
        }else if(res.status === config.forbidden){
          message.error("登录过期，请重新登录！");
        }else{
          message.error("服务器错误，稍后再试！");
        }
      })
    }
  }

  setActivatePage = key => {
    this.setState({activatePageKey: key})
  }

  clickLogin = (save) => {
    this.setState({
      loginModalVisible: true,
      save
    })
  }

  clickLogout = () => {
    this.setState({
      logoutModalVisible: true
    })
  }

  login = (save) => {
    this.formRef.current.validateFields().then(values => {
      const {userName, pwd} = values;

      axios.post(`${config.baseAddress}/login`, {userName, pwd})
      .then(res => {
        if(res.data.status){
          this.setState({userName, loginModalVisible: false});
          this.props.login(userName);

          const token = res.data.token;
          localStorage.setItem('token', token);

          if(save){
            this.picwall.save(true);
          }
        }else{
          message.error("登录失败！");
        }
      })
    })
  }

  handleLogout = () => {
    this.props.logout();
    localStorage.removeItem('token');
    this.setState({logoutModalVisible: false, userName: ""});
    window.location = "/"
  }

  handleCancel = () => {
    this.setState({
      loginModalVisible: false,
      logoutModalVisible: false,
    })
  }

  renderBreadCum = () => {
    if(this.picwall){
      const {activatePageKey, } = this.state;
      if(activatePageKey === '1' || activatePageKey === '2'){
        if(activatePageKey === '1'){
          let diagnosing = this.picwall.returnDiagnosing();
          if(diagnosing){
            return(
              <Breadcrumb style={{ margin: '16px 0' }}>
                <Breadcrumb.Item>Home</Breadcrumb.Item>
                <Breadcrumb.Item>上传图片</Breadcrumb.Item>
                <Breadcrumb.Item>诊断</Breadcrumb.Item>
              </Breadcrumb>
            )
          }else{
            return (
              <Breadcrumb style={{ margin: '16px 0' }}>
                <Breadcrumb.Item>Home</Breadcrumb.Item>
                <Breadcrumb.Item>上传图片</Breadcrumb.Item>
              </Breadcrumb>
            )
          }
        }else{
          if(this.userupload){
              let label = this.userupload.returnLabeling();
              if(label){
                return(
                  <Breadcrumb style={{ margin: '16px 0' }}>
                    <Breadcrumb.Item>Home</Breadcrumb.Item>
                    <Breadcrumb.Item>上传图片</Breadcrumb.Item>
                    <Breadcrumb.Item>标签</Breadcrumb.Item>
                  </Breadcrumb>
                )
              }else{
                return(
                  <Breadcrumb style={{ margin: '16px 0' }}>
                    <Breadcrumb.Item>Home</Breadcrumb.Item>
                    <Breadcrumb.Item>上传图片</Breadcrumb.Item>
                  </Breadcrumb>
                )
              }
          }
        }
      }else{
        return (
          <Breadcrumb style={{ margin: '16px 0' }}>
            <Breadcrumb.Item>Home</Breadcrumb.Item>
            <Breadcrumb.Item>历史记录查询</Breadcrumb.Item>
          </Breadcrumb>
        )
      }
    }
  }

  render() {
    const {userName, loginModalVisible, logoutModalVisible, activatePageKey, save} = this.state;
    const menu = userName === ""?(
      <Menu>
        <Menu.Item key="0" onClick={() => this.clickLogin(false)}>
          登录
        </Menu.Item>
      </Menu>
    ):(
      <Menu>
        <Menu.Item key="0" onClick={this.clickLogout}>
          退出
        </Menu.Item>
      </Menu>
    );

    return (
      <Layout className="App">
        <Header className="header">
          <div className="logo" >
            <Title style={{color: 'white', padding: '5px '}}>智能医疗辅助系统</Title>
          </div>
          <div className="userArea">
            <Dropdown overlay={menu}>
              <div>
              <Avatar className="avatar" size={50} icon={<UserOutlined />} style={{margin: '0 10px 5px 0'}}/>
                {userName}
              </div>
            </Dropdown>
          </div>
        </Header>
        <Router>
        <Content style={{ padding: '0 50px' }}>
          {this.renderBreadCum()}
          <Layout className="site-layout-background" style={{ padding: '24px 0', height: '90%'}}>
            <Sider className="site-layout-background" width={200}>
              <Menu
                mode="inline"
                defaultSelectedKeys={['1']}
                defaultOpenKeys={['sub1']}
                style={{ height: '100%' }}
                selectedKeys={activatePageKey}
              >
                <Menu.Item key="1" onClick={() => this.setActivatePage("1")}><UserOutlined/><Link to={"/"}>脑颅CT辅助诊断</Link></Menu.Item>
                {userName === ''?null: <Menu.Item key="2" onClick={() => this.setActivatePage("2")}><LaptopOutlined/><Link to={"/CTMaterialUpload"}>CT资料上传</Link></Menu.Item>}
                {userName === ''?null: <Menu.Item key="3" onClick={() => this.setActivatePage("3")}><NotificationOutlined/><Link to={"/history"}>历史诊断记录查询</Link></Menu.Item>}
              </Menu>
            </Sider>
              <Content style={{ padding: '0 24px', minHeight: 280 }}>
                <Switch>
                  <Route path="/CTMaterialUpload" render={props => <UserUpload onRef={ref => (this.userupload = ref)} setActivatePageKey={this.setActivatePage} {...props}></UserUpload>}/>
                  <Route path="/history" render={(props) => <HistoryBoard setActivatePageKey={this.setActivatePage} {...props}/>}/>
                  <Route exact path="/" render={(props) => <PicWall onRef={ref => (this.picwall = ref)} setActivatePageKey={this.setActivatePage} userLogin={this.clickLogin} {...props}/>} />
                </Switch>
              </Content>
          </Layout>
        </Content>
        </Router>
        <Footer style={{ textAlign: 'center' }}>Medical Support System Created by 张立辉</Footer>
        <Modal
          title="登录"
          visible={loginModalVisible}
          onCancel={this.handleCancel}
          okButtonProps={{onClick: () => this.login(save)}}
          okText="登录"
          cancelText="取消"
        >
          <Form
            ref={this.formRef}
            onFinish={this.login}
          >
            <Form.Item
              label="用户名"
              name="userName"
              rules={[{ required: true, message: '输入用户名' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              label="密码"
              name="pwd"
              rules={[{ required: true, message: '密码' }]}
            >
              <Input.Password
                style={{width: "405px", margin: "0 0 0 13px"}}
              />
            </Form.Item>
          </Form>
        </Modal>
        <Modal
          title="登出"
          cancelText="取消"
          onCancel={this.handleCancel}
          okText="确认"
          okButtonProps={{danger: true}}
          onOk={this.handleLogout}
          visible={logoutModalVisible}
        >
          确认登出系统？
        </Modal>
      </Layout>
    )
  }
}

const mapStateToProps = state => ({
  userName: state.userName
})

const mapDispatchToProps = dispatch => ({
  login(userName){
    dispatch({ type: 'LOGIN', data: {userName}});
  },
  logout(){
    dispatch({ type: 'LOGOUT'})
  }
})

export default connect(mapStateToProps, mapDispatchToProps)(App);