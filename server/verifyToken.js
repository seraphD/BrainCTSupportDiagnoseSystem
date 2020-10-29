function verifyToken(req, res, next) {
  const bareHead = req.headers['authorization'];

  if(typeof bareHead !== 'undefined') {
    const bare = bareHead.split(' ');
    const bareToken = bare[1];
    req.token = bareToken;
    next();
  }else{
    res.sendStatus(403)
  }
}

module.exports = verifyToken;