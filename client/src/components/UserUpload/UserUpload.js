import React from 'react';
import {connect} from 'react-redux';
import './UserUpload.css';
import {Upload, message, Modal, Button} from 'antd';
import {PlusOutlined} from '@ant-design/icons';
import axios from 'axios';
import config from '../../config.js';

function getBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
}
  

class UserUpload extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            fileList: [],
            uploading: false,
            uploaded: false,
            previewVisible: false,
            axisPreviewVisible: false,
            labeled: false,
            labelVisible: false,
            imgOnLabel: false,
            abnormal: [],
            normal: [],
            imgOnLabelIndex: -1,
        }
    }

    componentDidMount(){
        this.props.setActivatePageKey('2');
        this.props.onRef(this)
    }

    handleCancel = () => this.setState({
        previewVisible: false,
        axisPreviewVisible: false,
        labelVisible: false,
    });

    handlePreview = async file => {
        if (!file.url && !file.preview) {
          file.preview = await getBase64(file.originFileObj);
        }
    
        this.setState({
          previewImage: file.url || file.preview,
          previewVisible: true,
        });
    };

    handleChange = ({ fileList }) => this.setState({ fileList });

    beforeUpload = file => {
        this.setState(state => ({
            fileList: [...state.fileList, file]
        }))
        return false;
    }

    handleUpload = () => {
        const {normal, abnormal} = this.state;
        let formData = new FormData();
        this.setState({uploading: true});

        for(let i=0; i < normal.length; i++) {
            formData.append("normalfiles[]", JSON.stringify(normal[i]));
        }

        for(let i=0; i < abnormal.length; i++) {
            formData.append("abnormalfiles[]", JSON.stringify(abnormal[i]));
        }

        const token = localStorage.getItem("token");
        axios.post(`${config.baseAddress}/userUpload`, formData, {
            headers: {authorization: "bare " + token}
        })
        .then(res => {
          if(res.status === config.success){
            message.success("上传成功！");

            this.setState({uploaded: true});
          }else{
            message.error("上传失败！");
            this.setState({uploading: false});
          }
        })
    }

    startLabel = async () => {
        if(this.state.fileList.length === 0) {
            message.error("请先加载图片！");
            return;
        }

        const file = this.state.fileList[0];
        if (!file.url && !file.preview) {
            file.preview = await getBase64(file.originFileObj);
        }

        this.setState({
            labelVisible: true,
            imgOnLabelIndex: 0,
            imgOnLabel: file.url || file.preview
        })
    }

    label = async isNormal => {
        let {imgOnLabelIndex, normal, abnormal, fileList} = this.state;
        if(imgOnLabelIndex < fileList.length-1){
            if(isNormal){
                normal.push(fileList[imgOnLabelIndex]);
            }else{
                abnormal.push(fileList[imgOnLabelIndex]);
            }
    
            imgOnLabelIndex += 1;
    
            const file = fileList[imgOnLabelIndex];
            if (!file.url && !file.preview) {
                file.preview = await getBase64(file.originFileObj);
            }
            this.setState({
                imgOnLabelIndex,
                imgOnLabel: file.url || file.preview,
                normal,
                abnormal,
            })
        }else{
            this.setState({
                labelVisible: false,
                labeled: true,
            })
        }
    }

    returnLabeling = () => {
        const {labelVisible, labeled} = this.state;
        return labelVisible || labeled;
    }

    reset = () => {
        this.setState({
            fileList: [],
            uploading: false,
            uploaded: false,
            previewVisible: false,
            axisPreviewVisible: false,
            labeled: false,
            labelVisible: false,
            imgOnLabel: false,
            abnormal: [],
            normal: [],
            imgOnLabelIndex: -1,
        })
    }

    render() {
        const {fileList, previewVisible, previewImage, labeled, labelVisible, imgOnLabel, uploading, uploaded} = this.state;
        const uploadButton = (
            <div>
              <PlusOutlined />
              <div className="ant-upload-text">Upload</div>
            </div>
        );
        const button = !labeled? (
            <Button 
              type="primary"
              onClick={this.startLabel}
              className="btn"
            >
              开始标签
            </Button>
        ): !uploaded?(
            <Button 
                type="primary"
                onClick={this.handleUpload}
                loading={uploading}
                className="btn"
            >
                上传
            </Button>
        ): (
            <Button 
                type="primary"
                onClick={this.reset}
                className="btn"
            >
                重置
            </Button>
        )
        

        return(
            <div className="clearfix">
                <div className="upload-area">
                <Upload
                    listType="picture-card"
                    fileList={fileList}
                    onPreview={this.handlePreview}
                    onChange={this.handleChange}
                    beforeUpload={this.beforeUpload}
                    directory
                >
                    {fileList.length >= 8 ? null : uploadButton}
                </Upload>
                </div>
                <div style={{width: '100%', textAlign: 'center'}}>
                    {button}
                </div>
                <Modal visible={previewVisible} footer={null} onCancel={this.handleCancel}>
                    <img alt="example" style={{ width: '100%' }} src={previewImage} />
                </Modal>
                <Modal visible={labelVisible} footer={null} onCancel={this.handleCancel}>
                    <img alt="example" style={{ width: '100%' }} src={imgOnLabel} />
                    <div style={{width: '100%'}}>
                        <Button type="primary" className="operateBtn" onClick={() => this.label(true)}>正常</Button>
                        <Button type="primary" danger className="operateBtn" onClick={() => this.label(false)}>异常</Button>
                    </div>
                </Modal>
            </div>
        )
    }
}

const mapStateToProps = state => ({
    userName: state.userName
})

export default connect(mapStateToProps, null)(UserUpload);