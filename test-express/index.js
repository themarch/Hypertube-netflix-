let pug = require('pug');
let fs = require('fs');
const express = require('express');
const app = express();
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('../hypertube/db.sqlite3');
var torrentStream = require('torrent-stream');
const path = require('path');
const parseRange = require('range-parser');
const OpenSubtitles = require('opensubtitles-api');
const zlib = require('zlib')
var FfmpegCommand = require('fluent-ffmpeg');
var rimraf = require("rimraf");
var schedule = require('node-schedule');

const OS = new OpenSubtitles({
    useragent:'TemporaryUserAgent',
    username: 'hypertubebtt',
    password: 'Fakeuser0',
    ssl: true
});


var j = schedule.scheduleJob('0 4 * * *', function(){ // tous les jours a 4h du matin : 0 4 * * *
    db.all("SELECT * FROM video_torrent", function(err,rows){
        let date_ob = new Date();
        mydate = String(date_ob.getDate()) + '/' + String(date_ob.getMonth() + 1)
        rows.forEach(function (row) {
            if (row.watch_date){
                if (!row.watch_date.includes("/")){
                    let data = [mydate, row.idimdb];
                    let sql = `UPDATE video_torrent
                            SET watch_date = ?
                            WHERE idimdb = ?`;
                    db.run(sql, data, function(err) {
                        if (err) {
                            return console.error(err.message);
                        }              
                    });
                }
                parsed = row.watch_date.split('/');
                if (parsed[1] != String(date_ob.getMonth() + 1) && parseInt(parsed[0]) >= String(date_ob.getDate())) { // si le mois stocke en DB est different du mois actuel et que le jour stocke en db >= jour actuel
                    const url = row.idimdb;
                    let path_movie = "./video/" + url;
                    console.log(path_movie);
                    fs.access(path_movie, function(error) {
                        if (error) {
                            console.log("Directory does not exist: " + path_movie);
                        } else {
                            console.log("Directory exists: " + path_movie);
                            rimraf(path_movie, function () { console.log("... Deleted !"); });
                        }
                    })
                }
            }
        });
    });
});

app.use(express.static('video'));

app.get('/', function(req, res) {
    return res.redirect('http://localhost:8000');
    res.end() 
    })

app.get('/playserie', function(req, res) {
    film = req.query.film
    lang = req.query.lang
    season = req.query.season
    episode = req.query.episode
    vttname = 'subtitles/' + film + '_s' + season +  '_e' + episode + '_' + lang + '.vtt'
    if(!fs.existsSync(vttname)){
        const out = fs.createWriteStream(vttname);
        OS.search({
            imdbid: film,
            season: season,
            episode: episode,
            sublanguageid: lang,
            gzip: true
        }).then(subtitles => {
            if (lang in subtitles) {
                require('request')({
                    url: subtitles[lang]['vtt'],
                    encoding: null
                })
                .pipe(out)
            } else {
                throw 'no subtitle found';
            }
        }).catch(console.error);
        
    }
    try {
        console.log('------------------------------------3')
        files = fs.readdirSync('subtitles');
        p = []
        for (var i = 0; i < files.length; i++){
            if (files[i].search(film) != -1){
                tup = files[i].split('_')
                console.log(tup)
                console.log('tuuuuuuuuuup')
                la = tup[3].split('.')
                ep = '_s' + season + '_e' + episode + '_'
                console.log(ep)
                if (files[i].search(ep) != -1){
                p.push([files[i], tup[0], la[0]])
                }
            }
        }
      } catch(err) {
        // An error occurred
        console.error(err);
      }
      vid = db.get("SELECT `episodes` FROM video_torrent WHERE `idimdb`= ? ", [film], function(err, row) {
        try {
            suite = film + '_s' + season + '_e' + episode
            search = JSON.parse(row.episodes)
            for(var i = 0; i < search.length; i++ ){
                if (search[i]['episode'] == episode && search[i]['season'] == season){
                    vid = search[i]['torrents']['0']['url']
                    break;

                }
            }
            console.log(vid)
            var pa = './video/' + suite
            console.log(pa)
            const engine = torrentStream(vid)
            engine.on('ready', function(){
                engine.files.forEach(function (file, idx) {
                    const ext = path.extname(file.name).slice(1);
                    console.log(ext)
                    if (ext === 'mkv' || ext === 'mp4') {
        
                        file.ext = ext;
                        current = pa + '/' + file.path
                        console.log(current)
                        try{
                            const stats = fs.statSync(current);
                            console.log(stats)
                            const fileSizeInBytes = stats.size;
                            console.log(fileSizeInBytes)
                            console.log(file.length)
                            if (fileSizeInBytes == file.length){
                                console.log('boulou')
                                base = film + '_s' + season + '_e' + episode +  '/' + file.path
                                console.log(base)
                                console.log(pa)
                                console.log(ext)
                                if (ext == 'mkv'){
                                    exty = 'video/mp4'
                                }
                                else if (ext == 'mp4'){
                                    exty = 'video/mp4'
                                }
                                res.render(path.join(__dirname + '/video.ejs'), {base : base, film : film, lang : lang, files : p, exty : exty })
                            }

                        } 
                        catch (err) {
                            console.log(err.code)
                            if (err.code === 'ENOENT'){
                            console.log(ext)
                            if (ext == 'mkv'){
                                exty = 'video/mp4'
                            }
                            else if (ext == 'mp4'){
                                exty = 'video/mp4'
                            }
                            base = 'http://localhost:3000/SERIE?film=' + film + '&season=' + season + '&episode=' + episode + '&lang=' + lang 
                                res.render(path.join(__dirname + '/video.ejs'), {base : base, film : film, lang : lang, files : p, exty : exty })
                            }  
                        }
        
                    }
                });
            });
            }
    catch {
        return res.redirect('http://localhost:8000')
        res.end() 
    }
    }); // M
    
    })


app.get('/play', function toto(req, res) {
    console.log('------------------------------------1')
    film = req.query.film
    lang = req.query.lang
    token1 = req.query.tok
    console.log('TOKEN1 = ' + token1)
    tok1 = db.get("SELECT `token` FROM users_profile WHERE `token`= ?", [token1], function(err, row) {
        try {
            console.log(row.token)
        }
        catch (err) {
            return res.redirect('http://localhost:8000')
            res.end() 
        }

    });
    if (lang != 'fr' && lang != 'en' && lang != 'it') {
        return res.redirect('http://localhost:8000')
        res.end() 
    }
    vttname = 'subtitles/' + film + '_' + lang + '.vtt'
    console.log('------------------------------------2')
    if (!fs.existsSync(vttname)){
        const out = fs.createWriteStream(vttname);
        OS.search({
            imdbid: film,
            sublanguageid: lang,
            gzip: true
        }).then(subtitles => {
            if (lang in subtitles) {
                console.log('Subtitle found:', subtitles);
                require('request')({
                    url: subtitles[lang]['vtt'],
                    encoding: null
                })
                .pipe(out)
            } else {
                throw 'no subtitle found';
            }
        }).catch(console.error);

    }
    try {
        console.log('------------------------------------3')
        files = fs.readdirSync('subtitles');
        p = []
        for (var i = 0; i < files.length; i++){
            if (files[i].search(film) != -1){
                tup = files[i].split('_')
                la = tup[1].split('.')
                p.push([files[i], tup[0], la[0]])
            }
        }
        console.log(p)
      } catch(err) {
        // An error occurred
        console.error(err);
      }
      vid = db.get("SELECT `magnets` FROM video_torrent WHERE `idimdb`= ? ", [film], function(err, row) {
        try {
            var vid = row.magnets
            var pa = './video/' + film
            const engine = torrentStream(vid)
            engine.on('ready', function(){
                engine.files.forEach(function (file, idx) {
                    const ext = path.extname(file.name).slice(1);
                    if (ext === 'mkv' || ext === 'mp4') {
        
                        file.ext = ext;
                        current = pa + '/' + file.path
                        console.log(current)
                        try{
                            const stats = fs.statSync(current);
                            console.log(stats)
                            const fileSizeInBytes = stats.size;
                            console.log(fileSizeInBytes)
                            console.log(file.length)
                            if (fileSizeInBytes == file.length){
                                console.log('boulou')
                                if (ext == 'mkv'){
                                    exty = 'video/mp4'
                                }
                                else if (ext == 'mp4'){
                                    exty = 'video/mp4'
                                }
                                base = film + '/' + file.path
                                console.log(current)
                                res.render(path.join(__dirname + '/video.ejs'), {base : base, film : film, lang : lang, files : p, exty : exty })
                            }

                        } 
                        catch (err) {
                            console.log(err.code)
                            if (err.code === 'ENOENT'){
                            console.log('download')
                            if (ext == 'mkv'){
                                exty = 'video/mp4'
                            }
                            else if (ext == 'mp4'){
                                exty = 'video/mp4'
                            }
                            base = 'http://localhost:3000/BDD?film=' + film + '&lang=' + lang 
                                res.render(path.join(__dirname + '/video.ejs'), {base : base, film : film, lang : lang, files : p , exty : exty})
                            }
                        }
        
                    }
                });
            });
        }
        catch (err) {
            return res.redirect('http://localhost:8000')
            res.end() 
        }
    }); // M
    
    })

app.get('/BDD', function (req, res) {
    try {
        console.log('first fonction app use');
            console.log(req.url)
            film = req.query.film
                console.log(film)
                vid = db.get("SELECT `magnets` FROM video_torrent WHERE `idimdb`= ? ", [film], function(err, row) {
                var vid = row.magnets
                var pa = './video/' + film
                const engine = torrentStream(vid, {path : pa});
                const getTorrentFile = new Promise(function (resolve, reject) {
                    engine.on('ready', function(){
                        engine.files.forEach(function (file, idx) {
                            const ext = path.extname(file.name).slice(1);
                            if (ext === 'mkv' || ext === 'mp4') {
                
                            console.log('download')
                                    resolve(file);
            
                                
                
                            }
                        });
                    });
                }); // M
            addresse = '/BDD?film=' + film + '&lang=' + lang
            if (req.url != addresse) 
                {
                console.log('pouloulou')
                console.log(req.url)
                res.setHeader('Content-Type', 'text/html');
                if (req.method !== 'GET') return res.end();
                var rpath = __dirname + '/video.html';
                console.log(rpath)
                fs.readFile(rpath, 'utf8', function (err, str) {
                    var fn = pug.compile(str, { filename: rpath, pretty: true});
                    res.end(fn());
                });
            } else {
                    console.log('ding')
                    res.setHeader('Accept-Ranges', 'bytes');
                    let date_ob = new Date();
                    mydate = String(date_ob.getDate()) + '/' + String(date_ob.getMonth() + 1)
                    console.log(mydate);
                    console.log(film)
                    let data = [mydate, film];
                    let sql = `UPDATE video_torrent
                            SET watch_date = ?
                            WHERE idimdb = ?`;
                    db.run(sql, data, function(err) {
                    if (err) {
                        return console.error(err.message);
                    }
                    console.log(`Row(s) updated: ${this.changes}`);
                    
                    });
                    getTorrentFile.then(function (file) {
                        res.setHeader('Content-Length', file.length);
                        res.setHeader('Content-Type', `video/${file.ext}`);
                    const ranges = parseRange(file.length, '15' /* variable à comprendre */, { combine: true });
                    console.log('ranges');
                    if (ranges === -1) {
                        // 416 Requested Range Not Satisfiable
                        console.log('416')
                        res.statusCode = 416;
                        return res.end();
                    } else if (ranges === -2 || ranges.type !== 'bytes' || ranges.length > 1) {
                        // 200 OK requested range malformed or multiple ranges requested, stream ent'ire video
                        if (req.method !== 'GET') return res.end();
                        console.log('200')
                        file.createReadStream().pipe(res);
                    } else {
                        // 206 Partial Content valid range requested
                        console.log('206')
                        const range = ranges[0];
                        res.statusCode = 206;
                        res.setHeader('Content-Length', 1 + range.end - range.start);
                        res.setHeader('Content-Range', `bytes ${range.start}-${range.end}/${file.length}`);
                        if (req.method !== 'GET') return res.end();
                        file.createReadStream(range).pipe(res);    
                    }
                }).catch(function (e) {
                    console.error(e);
                    res.end(e);
                });
        }
            });	
            console.log(vid)
        }
        catch (err) {
            console.log('rip')
        }     
    });

app.get('/SERIE', function (req, res) {
    try {
        console.log('first fonction app use');
            console.log(req.url)
            film = req.query.film
            season = req.query.season
            episode = req.query.episode
                console.log(film)
                vid = db.get("SELECT `magnets` FROM video_torrent WHERE `idimdb`= ? ", [film], function(err, row) {
                var vid = row.magnets
                var pa = './video/' + film + '_s' + season + '_e' + episode
                const engine = torrentStream(vid, {path : pa})
                const getTorrentFile = new Promise(function (resolve, reject) {
                    engine.on('ready', function(){
                        engine.files.forEach(function (file, idx) {
                            const ext = path.extname(file.name).slice(1);
                            if (ext === 'mkv' || ext === 'mp4' || ext === 'avi') {
                
                            console.log('download')
                                    resolve(file);
                                    
                                
                
                            }
                        });
                    });
                }); // M
            addresse = '/SERIE?film=' + film + '&season=' + season + '&episode=' + episode + '&lang=' + lang
            if (req.url != addresse) 
                {
                console.log('pouloulou')
                console.log(req.url)
                res.setHeader('Content-Type', 'text/html');
                if (req.method !== 'GET') return res.end();
                var rpath = __dirname + '/video.html';
                console.log(rpath)
                fs.readFile(rpath, 'utf8', function (err, str) {
                    var fn = pug.compile(str, { filename: rpath, pretty: true});
                    res.end(fn());
                });
            } else {
                    console.log('ding')
                    res.setHeader('Accept-Ranges', 'bytes');
                    getTorrentFile.then(function (file) {
                        res.setHeader('Content-Length', file.length);
                        res.setHeader('Content-Type', `video/${file.ext}`);
                    const ranges = parseRange(file.length, '15' /* variable à comprendre */, { combine: true });
                    console.log('ranges');
                    if (ranges === -1) {
                        // 416 Requested Range Not Satisfiable
                        console.log('416')
                        res.statusCode = 416;
                        return res.end();
                    } else if (ranges === -2 || ranges.type !== 'bytes' || ranges.length > 1) {
                        // 200 OK requested range malformed or multiple ranges requested, stream ent'ire video
                        if (req.method !== 'GET') return res.end();
                        console.log('200')
                        file.createReadStream().pipe(res);
                    } else {
                        // 206 Partial Content valid range requested
                        console.log('206')
                        const range = ranges[0];
                        res.statusCode = 206;
                        res.setHeader('Content-Length', 1 + range.end - range.start);
                        res.setHeader('Content-Range', `bytes ${range.start}-${range.end}/${file.length}`);
                        if (req.method !== 'GET') return res.end();
                        file.createReadStream(range).pipe(res);    
                    }
                }).catch(function (e) {
                    console.error(e);
                    res.end(e);
                });
        }
            });	
            console.log(vid)     
        }
        catch (err) {
            console.log('rip2')
        }   
});

app.use('/subtitles/:idimdb/:lang', function(req, res){
    console.log('polo')
    var filename = __dirname+req.url;

    // This line opens the file as a readable stream
    add = 'subtitles/' + req.params.idimdb
    var readStream = fs.createReadStream(add);
  
    // This will wait until we know the readable stream is actually valid before piping
    readStream.on('open', function () {
      // This just pipes the read stream to the response object (which goes to the client)
      readStream.pipe(res);
    });
  
    // This catches any errors that happen while creating the readable stream (usually invalid names)
    readStream.on('error', function(err) {
      res.end(err);
    });

})

app.get('/movie', function(req, res) {
    
    res.sendFile(path.join(__dirname + '/movie.ejs'))
    })

app.get('*', function(req, res){
    return res.redirect('http://localhost:8000');
    res.end() 
    });

app.listen(process.env.port || 3000);

console.log('Running at Port 3000');