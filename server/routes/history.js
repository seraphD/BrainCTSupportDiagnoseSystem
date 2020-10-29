var express = require('express');
var router = express.Router();
const verifyToken = require('../verifyToken.js');
const jwt = require('jsonwebtoken');
const fs = require('fs');
const pool = require("../mysqlConnect.js");
const urlModule = require('url');
const secretkey = require("../secretkey.js");

router.use(express.json())
router.use(express.urlencoded({ extended: false }))

function copyFile(src, dst) {
    return new Promise((resolve, reject) => {
        fs.readdir(src, (err, currentFiles) => {
            currentFiles.forEach(file => {
                fs.writeFileSync(dst+"/"+file, fs.readFileSync(src+"/"+file))
            })
        })
        return resolve();
    })
}

function saveResult(userName, date, index, result){
    return new Promise((resolve, reject) =>{

        pool.query(`insert into results values('${userName}', '${date}', '${index}', '${result}')`, (err, results) =>{
            if(err) return reject(err)
        })

        return resolve();
    })
}

function getHistoryRecord(userName){
    return new Promise((resolve, reject) => {
        
        pool.query(`select date, fileIndex from results where userName='${userName}' ORDER BY date DESC`, (err, results, field) => {
            if(err)return reject(err)
            else{
                let record = {}
                for(let result of results){
                    const {date, fileIndex} = result;

                    if(typeof record[date] === "undefined"){
                        record[date] = []
                    }

                    record[date].push(fileIndex)
                }
                return resolve(record)
            }
        })

    })
}

function getRecordResult(userName, date, index){
    return new Promise((resolve, reject) => {

        pool.query(`select result from results where userName='${userName}' and date='${date}' and fileIndex='${index}'`, (err, results) => {
            if(err)return reject(err);
            else{
                return resolve(results[0]['result']);
            }
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

function getPicsData(dirpath){
    return new Promise((resolve, reject) => {
        let pics = []
        fs.readdir(dirpath,async (err, currentFiles) => {
            if(err)return reject(err)
            else{
                currentFiles.forEach(async (file) => {
                    let picData = await getBase64(`${dirpath}/${file}`).catch(err => console.log(err))
                    pics.push(picData);
                })

                return resolve(pics);
            }
        })
    })
}

function reviseResult(userName, date, fileIndex, newResult){
    return new Promise((resolve, reject) => {

        pool.query(`update results set result='${newResult}' where userName='${userName}' and date='${date}' and fileIndex='${fileIndex}'`,
        (err, results, field) => {
            if(err)return reject(err)
            else{
                return resolve();
            }
        })

    })
}

router.get('/getRecord', verifyToken, (req, res) => {
    jwt.verify(req.token, secretkey, async (err, authData) => {
        if(err)res.sendStatus(500)
        else {
            const {userName} = authData;

            let record = await getHistoryRecord(userName).catch(err => res.sendStatus(500))
            
            res.json(record)
        }
    })
})

router.post('/saveResult', verifyToken,async (req, res) => {
    const {result, filepath, copy} = req.body;
    jwt.verify(req.token, secretkey,async (err, authData) => {
        if(err)res.sendStatus(403)
        else{
            let {userName} = authData;
            let info = filepath.split("CT")[1].split("/");
            let date = info[2];
            let index = info[3];

            if(copy){
                    fs.readdir(`/home/lihui/medical-support/server/python/CT/${userName}/${date}`,async (err, crtFiles) => {
                        if(err){
                            fs.mkdirSync(`/home/lihui/medical-support/server/python/CT/${userName}/${date}`)
                            crtFiles = []
                        }

                        fs.mkdirSync(`/home/lihui/medical-support/server/python/CT/${userName}/${date}/${crtFiles.length}`, (err) => console.log(err))
                        index = crtFiles.length
                        await copyFile(`/home/lihui/medical-support/server/python/CT/anonymity/${date}/${index}`, 
                        `/home/lihui/medical-support/server/python/CT/${userName}/${date}/${crtFiles.length}`).catch(err => console.log(err))
                        await saveResult(userName, date, index, result).catch(err => res.sendStatus(500));
                        res.json({path: date + "-" + index})
                    })
            }else{
                await saveResult(userName, date, index, result).catch(err => res.sendStatus(500));
                res.json({path: date + "-" + index})
            }
        }
    })
});

router.get("/recordDetail", verifyToken, (req, res) => {
    jwt.verify(req.token, secretkey, async (err, authData) => {
        let {userName} = authData;
        let params = urlModule.parse(req.url, true).query;
        const {date, fileIndex} = params;

        let diagnoseResult = await getRecordResult(userName, date, fileIndex).catch(err => res.sendStatus(500));
        let dirpath = `/home/lihui/medical-support/server/python/CT/${userName}/${date}/${fileIndex}`;

        let pics = await getPicsData(dirpath).catch(err => res.sendStatus(500))
        res.json({diagnoseResult, pics});        
    })
})

router.post("/reviseResult", verifyToken, (req, res) => {
    jwt.verify(req.token, secretkey, async (err, authData) => {
        if(err)res.sendStatus(403)
        else{
            let {userName} = authData;
            let {date, fileIndex, diagnoseResult} = req.body;

            await reviseResult(userName, date, fileIndex, diagnoseResult).catch(err => res.sendStatus(500))
            res.sendStatus(200)
        }
    })
})

module.exports = router;