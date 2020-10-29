import React from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import config from '../../config.js';
import {message, Layout, Tree} from 'antd';
import RecordDetail from '../RecordDetail/RecordDetail.js';

const { Content, Sider } = Layout;
const { DirectoryTree } = Tree;

class HistoryBoard extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            treeData: [],
            selectedKey: "",
        }
    }

    componentDidMount(){
        this.props.setActivatePageKey("3");

        const token = localStorage.getItem('token');
        axios.get(`${config.baseAddress}/history/getRecord`, {
            headers: {authorization: "bare " + token}
          }).then(res => {
            if(res.status === config.success){
                const record = res.data;
                let treeData = []
                
                for(let date in record){
                    let children = []
                    for(let fileIndex of record[date]){
                        children.push({
                            key: `${date}-${fileIndex}`,
                            title: fileIndex,
                            isLeaf: true,
                        })
                    }

                    treeData.push({
                        title: date,
                        key: date,
                        children,
                    })
                }

                let key = this.props.location.pathname.split("/")[2];
                if(typeof key !== "undefined"){
                    this.setState({
                        selectedKey: key,
                    })
                }
                this.setState({treeData})
            }else if(res.status === config.forbidden){
                message.error("登陆过期，请重新登陆！");
            }else if(res.status === config.ServerError){
                message.error("服务器故障，请稍后再试！");
            }
          })
    }

    checkDeatil = (value) => {
        if(typeof value[0] === "undefined"){
            return;
        }

        let data = value[0].split("-")

        if(data.length === 3){
            return;
        }
        this.props.history.push(`/history/${value[0]}`)
        this.setState()
    }

    render(){
        const {treeData, selectedKey} = this.state;

        return (
            <div style={{height: '100%'}}>
                <Sider className="site-layout-background" width={200} style={{display: 'inline-block', verticalAlign: 'top'}}>
                   {treeData.length>0?<DirectoryTree
                    defaultExpandAll
                    treeData={treeData}
                    blockNode
                    onSelect={this.checkDeatil}
                    defaultSelectedKeys={[selectedKey]}
                    checkedKeys={[selectedKey]}
                    autoExpandParent
                   />: null}
                </Sider>
                <Content className="detailArea" style={{ overflowY: 'auto', padding: '0 24px', height: '100%', display: 'inline-block',width: '900px'}}>
                    <RecordDetail pathname={this.props.location.pathname}/>
                </Content>
            </div>
        )
    }
}

const mapStateToProps = state => ({
    userName: state.userName
})

export default connect(mapStateToProps, null)(HistoryBoard);