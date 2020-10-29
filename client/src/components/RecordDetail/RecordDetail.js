import React from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import config from '../../config.js';
import {message, Typography, Button, Modal, Input, Spin } from 'antd';
import './RecordDetail.css';

const { Title } = Typography;

class RecordDetail extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            loading: false,
            diagnoseResult: "",
            pics: [],
            reviseModalVisible: false,
            revising: false,
            tempDiagnoseResult: "",
            loaded: false,
        }
    }

    componentDidMount(){
        this.updateDeatial()
    }

    componentWillReceiveProps(nextProps){
        if(nextProps.pathname !== this.props.pathname){
            this.updateDeatial(nextProps.pathname);
        }
    }

    updateDeatial = (pathname) => {
        if(typeof pathname === "undefined"){
            pathname = this.props.pathname;
        }

        let data = pathname.split('/')[2];
        if(typeof data === "undefined"){
            return
        }
        data = data.split("-")
        
        let date = data.slice(0, 3).join("-");
        let fileIndex = data[3];
        const token = localStorage.getItem("token");
        this.setState({loading: true, loaded: false});
        axios.get(`${config.baseAddress}/history/recordDetail`, {
            headers: {authorization: "bare " + token},
            params: {
                date,
                fileIndex
            }
        }).then(res => {
            if(res.status === config.success){
                const {pics, diagnoseResult} = res.data;
                this.setState({loading: false, pics, diagnoseResult, tempDiagnoseResult: diagnoseResult, date, fileIndex, loaded: true});
            }else if(res.status === config.forbidden){
                message.error("登陆过期，请重新登陆！");
            }else if(res.status === config.ServerError){
                message.error("服务器故障，请稍后再试！");
            }
        })
    }

    changeResults = (e) => {
        this.setState({
          tempDiagnoseResult: e.target.value
        })
    }

    reviseResult = () => {
        const {tempDiagnoseResult, date, fileIndex} = this.state;
        const token = localStorage.getItem('token');

        axios.post(`${config.baseAddress}/history/reviseResult`, {diagnoseResult:tempDiagnoseResult, date, fileIndex}, {
            headers: {authorization: 'Bearer ' + token},
        }).then(res => {
            if(res.status === config.success){
                message.success("修改成功！");

                this.setState({
                    reviseModalVisible: false,
                    diagnoseResult: tempDiagnoseResult,
                })
            }else if(res.status === config.forbidden){
                message.error("登陆过期，请重新登陆！");
            }else if(res.status === config.ServerError){
                message.error("服务器故障，请稍后再试！");
            }
        })
    }

    render(){
        const {diagnoseResult, reviseModalVisible, loading, pics, revising, loaded} = this.state; 

        return (
            <div style={{height: '100%'}}>
                <div className="center">
                    <Title level={2}>参考诊断结果</Title>
                </div>
                <div>
                    {loading?<div className="center"><Spin style={{margin: '150px 0 0 0'}} size={"large"}/></div>:
                    <div>
                        <div className="resultbox">{diagnoseResult}</div>
                        <div className="center">
                            <div>
                            {pics.map((pic, i) => (
                                <img key={i} className="CTimgs" src={pic} alt="loading"></img>
                            ))}
                            </div>
                        </div>
                        <div className="center">
                            {loaded? <Button style={{width: "150px"}} type="primary" onClick={() => this.setState({reviseModalVisible: true})}>修改</Button>: null}
                        </div>
                    </div>
                    }
                </div>
                <Modal
                    title="修改诊断结果"
                    visible={reviseModalVisible}
                    onCancel={() => this.setState({reviseModalVisible: false})}
                    okText="确认"
                    cancelText="取消"
                    onOk={this.reviseResult}
                    okButtonProps={{loading: revising}}
                >
                    <Input.TextArea rows={4} defaultValue={diagnoseResult} onChange={this.changeResults}></Input.TextArea>
                </Modal>
            </div>
        )
    }
}

const mapStateToProps = state => ({
    userName: state.userName
})

export default connect(mapStateToProps, null)(RecordDetail);