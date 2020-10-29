import { Upload, Modal, Button, message, Select, Spin, Input } from 'antd';
import React from 'react';
import { PlusOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons';
import axios from 'axios';
import config from '../../config.js';
import './PicWall.css';
import { connect } from "react-redux";

const { Option } = Select;

function getBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
}

class PicturesWall extends React.Component {
  state = {
    previewVisible: false,
    previewImage: '',
    axisPreviewVisible: false,
    axisPreviewImage: '',
    fileList: [],
    uploading: false,
    filepath: '',
    uploaded: false,
    diagnosing: false,
    scale: 1,
    adjusting: false,
    diagnoseProcessing: false,
    result: "",
    processed: false,
    userName: '',
    resultModalVisible: false,
    revising: false,
    saving: false,
  };

  componentDidMount() {
    const { userName } = this.props;

    this.setState({ userName });
    this.props.setActivatePageKey("1");
    this.props.onRef(this)
  }

  handleCancel = () => this.setState({ previewVisible: false, axisPreviewVisible: false });

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
    const { fileList } = this.state;
    const { userName } = this.props;
    if (fileList.length === 0) {
      message.error('至少上传一张图片！')
      return;
    }

    let formData = new FormData();
    this.setState({ uploading: true });

    for (let i = 0; i < fileList.length; i++) {
      formData.append("files[]", JSON.stringify(fileList[i]));
    }

    formData.append("userName", userName);

    axios.post(`${config.baseAddress}/uploadPic`, formData)
      .then(res => {
        if (res.status === config.success) {
          message.success("上传成功！");

          let filepath = res.data.filepath;
          this.setState({ filepath, uploading: false, uploaded: true });
        } else {
          message.error("上传失败！");
          this.setState({ uploading: false });
        }
      })
  }

  runDiagnose = () => {
    let { filepath } = this.state;
    this.setState({ diagnosing: true });
    axios.get(`${config.baseAddress}/axisPreview`, {
      params: { filepath }
    }).then(res => {
      if (res.status === config.success) {
        let axisPreviewImage = res.data.axisPreview;
        this.setState({ axisPreviewVisible: true, diagnosing: false, axisPreviewImage });
      } else {
        message.error("对称轴预览失败，请重试！");
      }
    })
  }

  handleDegreeChangeScale = (scale) => {
    this.setState({ scale });
  }

  confirmAdjustment = () => {
    let { filepath } = this.state;
    this.setState({ diagnoseProcessing: true });

    axios.post(`${config.baseAddress}/confirmAxis`, { filepath })
      .then(res => {
        if (res.status === config.success) {
          let { diagnose } = res.data;

          this.setState({ resultModalVisible: true, diagnoseProcessing: false, result: diagnose, axisPreviewVisible: false, processed: true });
        } else {
          message.error("操作失败,请重试！");
        }
      })
  }

  adjust = (direction) => {
    let { scale, filepath, adjusting } = this.state;

    if (!adjusting) {
      this.setState({ adjusting: true })

      axios.post(`${config.baseAddress}/adjustAxis`, { filepath, direction, scale })
        .then(res => {
          if (res.status === config.success) {
            let axisPreviewImage = res.data.axisPreview;
            this.setState({ axisPreviewImage, adjusting: false });
          }
        })
    }
  }

  reset = () => {
    this.setState({
      previewVisible: false,
      previewImage: '',
      axisPreviewVisible: false,
      axisPreviewImage: '',
      fileList: [],
      uploading: false,
      filepath: '',
      uploaded: false,
      diagnosing: false,
      scale: 1,
      adjusting: false,
      diagnoseProcessing: false,
      result: "",
      processed: false,
    })
  }

  save = (copy) => {
    const { result, filepath } = this.state;
    this.setState({
      resultModalVisible: true,
    })

    this.setState({ saving: true });
    let token = localStorage.getItem('token');
    axios.post(`${config.baseAddress}/history/saveResult`, { result, filepath, copy }, {
      headers: { authorization: 'Bare ' + token }
    }).then(res => {
      if (res.status === config.success) {
        message.success("保存成功！");
        this.setState({ saving: false, resultModalVisible: false });
        let { path } = res.data;

        this.props.history.push(`/history/${path}`);
      } else if (res.status === config.forbidden) {
        message.error("登录失效！")
      } else if (res.status === config.ServerError) {
        message.error("服务器错误！");
      }
    })
  }

  saveResults = () => {
    const { userName } = this.props;

    if (userName === "") {
      message.error("请先登录！")

      this.setState({
        resultModalVisible: false,
      })

      this.props.userLogin(true);
    } else {
      this.save(false)
    }

  }

  reviseResults = () => {
    this.setState({ revising: true })
  }

  finishRevise = () => {
    this.setState({ revising: false })
  }

  changeResults = (e) => {
    this.setState({
      result: e.target.value
    })
  }

  returnDiagnosing = () => {
    const { diagnosing, diagnoseProcessing, processed } = this.state;
    return diagnosing || diagnoseProcessing || processed;
  }

  render() {
    const { previewVisible, previewImage, axisPreviewVisible,
      axisPreviewImage, adjusting, diagnoseProcessing, resultModalVisible,
      fileList, uploading, uploaded, diagnosing, processed, result, revising, saving } = this.state;
    const uploadButton = (
      <div>
        <PlusOutlined />
        <div className="ant-upload-text">Upload</div>
      </div>
    );
    const button = !uploaded ? (
      <Button
        type="primary"
        onClick={this.handleUpload}
        loading={uploading}
        className="btn"
      >
        上传
      </Button>
    ) : !processed ? (
      <Button
        type="primary"
        onClick={this.runDiagnose}
        loading={diagnosing}
        className="btn"
      >
        诊断
      </Button>
    ) : (
          <Button
            type="primary"
            onClick={this.reset}
            className="btn"
          >
            重置
          </Button>
        )
    const iconStyle = {
      fontSize: "50px",
    }
    const selectStyle = {
      width: "240px",
      margin: "10px 0 0 66px",
      verticalAlign: "top",
    }
    const confirmBntStyle = {
      width: "200px",
      margin: "0 0 0 136px"
    }
    return (
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
        <div style={{ width: '100%', textAlign: 'center' }}>
          {button}
        </div>
        <br />
        <div style={{ textAlign: 'left', fontSize: '1.5em', margin: '10px 0 0 0' }}>
          <a href={`${config.baseAddress}/downloadSample`} download>示例图片</a>
        </div>
        <Modal visible={previewVisible} footer={null} onCancel={this.handleCancel}>
          <img alt="example" style={{ width: '100%' }} src={previewImage} />
        </Modal>
        <Modal visible={axisPreviewVisible} footer={null} onCancel={this.handleCancel}>
          {adjusting ? <div style={{ width: '100%', textAlign: 'center', height: '451px' }}><Spin size="large" style={{ margin: '218px' }} /></div> : <img alt="example" style={{ width: '100%' }} src={axisPreviewImage} />}<br />
          <div style={{ padding: "10px 0 0 0" }}>
            <LeftOutlined style={iconStyle} onClick={() => this.adjust('left')} />
            <Select defaultValue="1x" onChange={this.handleDegreeChangeScale} style={selectStyle}>
              <Option value="1">1x</Option>
              <Option value="5">5x</Option>
              <Option value="10">10x</Option>
              <Option value="50">50x</Option>
            </Select>
            <RightOutlined style={{ ...iconStyle, float: 'right' }} onClick={() => this.adjust('right')} />
          </div>
          <Button
            type="primary"
            style={confirmBntStyle}
            onClick={this.confirmAdjustment}
            loading={diagnoseProcessing}
          >
            {diagnoseProcessing ? "诊断中" : "确认"}
          </Button>
        </Modal>
        <Modal
          title="诊断结果"
          visible={resultModalVisible}
          footer={revising ? <Button type="primary" onClick={this.finishRevise}>完成修改</Button> :
            <div><Button danger onClick={this.reviseResults}>修改</Button><Button type="primary" onClick={this.saveResults} loading={saving}>保存</Button></div>}
        >
          {revising ?
            <Input.TextArea rows={4} defaultValue={result} onChange={this.changeResults} />
            : <div>
              {result}
            </div>}
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  userName: state.userName
})

export default connect(mapStateToProps, null)(PicturesWall);