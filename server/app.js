const express = require('express');
const path = require('path');
const cores = require('cors');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const fs = require('fs');
const multer = require('multer');
const port = 3005;
const child_process = require('child_process');
const urlModule = require('url');
const request = require('request');
const iconv = require('iconv-lite');
const jwt = require('jsonwebtoken');
const historyRoutes = require('./routes/history.js');
const userUploadRoutes = require("./routes/userUpload.js");
const verifyToken = require('./verifyToken.js');
const secretkey = require("./secretkey.js");

const objMulter  = multer({dest:'./CT'});

var app = express();
const pool = require('./mysqlConnect.js');
app.use(cores());
app.use(objMulter.any());
app.use('/history', historyRoutes);
app.use('/userUpload', userUploadRoutes);

app.all('*', function(req, res, next) { 
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "X-Requested-With");
    res.header("Access-Control-Allow-Methods","PUT,POST,GET,DELETE,OPTIONS");
    res.header("X-Powered-By",' 3.2.1');
    res.header("Content-Type", "application/json;charset=utf-8");
    res.header('Access-Control-Allow-Credentials', true);
    next();
});

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static('sample'));

function saveFiles(files, cnt, path) {
  return new Promise((resolve, reject) => {
    fs.mkdir(`${path}/${cnt}`, err => {
        for(let file of files){
          file = JSON.parse(file);
          let filename = file.name;
          let base64Data = file.thumbUrl.replace(/^data:image\/\w+;base64,/, "");
          let dataBuffer = new Buffer(base64Data, 'base64');
          let newname = `${path}/${cnt}/${filename}`;
          
          fs.writeFile(newname, dataBuffer, err => {
            if(err){
              console.log(err);
            }
          })
        }
        resolve();
      });
  })
}

function findAxis(filepath) {
  return new Promise((resolve, reject) => {
    child_process.exec(`python ./python/findAxis.py --path="${filepath}"`, (err, stdout, stderr) => {
      if(err) return reject(err)
      else resolve(stdout);
    })
  })
}

function adjustAxis(filepath, direction, scale) {
  return new Promise((resolve, reject) => {
    child_process.exec(`python ./python/adjustAxis.py --path="${filepath}" --direction="${direction}" --scale="${scale}"`, (err, stdout, stderr) => {
      if(err) return reject(err)
      else return resolve(stdout);
    })
  })
}

function getBase64(file) {
  return new Promise((resolve, reject) => {
    let imageData = fs.readFileSync(file);
    let imgData64 = imageData.toString('base64');
    let prefix = "data:image/bmp;base64,";
    resolve(prefix + imgData64);
  });
}

function runDiagnose(filepath) {
  return new Promise((resolve, reject) => {
    child_process.exec(`python ./python/diagnose.py --path="${filepath}"`, { encoding: 'buffer' }, (err, stdout, stderr) => {
      if(err) return reject(err);
      else return resolve(iconv.decode(stdout, 'utf-8'));
    })
  })
}

function getDateStr(){
  let date = new Date();
  
  return `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`
}

function verifyPassword(userName, password){
  return new Promise((resolve, reject) => {
    pool.query(`select pwd from users where username='${userName}'`, (err,results, field) => {
        if(err)return reject(err)
        else{
            return resolve(password === results[0]['pwd'])
        }
    })
  })
}

// 获取对称轴预览图
app.get("/axisPreview", async (req, res, next) => {
  let params = urlModule.parse(req.url, true).query;
  let filepath = params.filepath;
  console.log(filepath);
  await findAxis(filepath);
  let axisPath = "./python/axis" + filepath.split("CT")[1]
  let imgWithAxis = await getBase64(axisPath + "/imgWithAxis.JPG");
  res.json({axisPreview: imgWithAxis})
})
// 上传图片
app.post("/uploadPic", (req, res, next) => {
    let {files, userName} = req.body;
    if(userName === ''){
      userName = "anonymity"
    }
    let dateStr = getDateStr();
    let path = `./python/CT/${userName}/${dateStr}`

    fs.readdir(path ,async (err, currentfiles) => {
      if(err){
        fs.mkdir(path, (err) => {
          if(err)console.log(err)
        })
        fs.mkdir(`./python/axis/${userName}/${dateStr}`, (err) => {
          if(err)console.log(err)
        })
        currentfiles = []
      }

      let cnt = currentfiles.length;
      await saveFiles(files, cnt, path);
      res.json({filepath: `${path}/${cnt}`})
    });
})
// 对称轴调整
app.post("/adjustAxis", async (req, res, next) => {
  let {filepath, direction, scale} = req.body;
  await adjustAxis(filepath, direction, scale)
  filepath = filepath.split("CT").join("axis")
  let imgWithAxis = await getBase64(`${filepath}/imgWithAxis.JPG`);
  res.json({axisPreview: imgWithAxis})
})
// 对称轴确认，开始诊断流程
app.post("/confirmAxis",async (req, res) => {
  let {filepath} = req.body;
  let diagnose = await runDiagnose(filepath)
  res.json({diagnose});
})
// 下载样例图片
app.get("/downloadSample", (req, res) => {
  const file = `./sample/sample.zip`;
  res.download(file); 
})
// jwt令牌自动登录
app.post('/autoLogin', verifyToken, (req, res) => {
  jwt.verify(req.token, secretkey, (err, authData) => {
    if(err){
      res.sendStatus(403)
    }else{
      res.json({
        status: true,
        authData
      })
    }
  })
})
// 用户登录
app.post('/login',async (req, res) => {
  const {userName, pwd} = req.body;

  if(await verifyPassword(userName, pwd)){
    jwt.sign({userName}, secretkey, {expiresIn: '7d'}, (err, token) => {
      res.json({status: true, token});
    })
  }else{
    res.json({status: false});
  }
})

app.listen(port, function () {
  console.log('Server is running on port ' + port);
});