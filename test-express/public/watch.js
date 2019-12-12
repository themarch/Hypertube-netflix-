a = document.getElementsByTagName('source')
a[0].addEventListener("playing", function(){
            param = window.location.search
            param = param.split('=')
            srclang2 = param[2]
            src2= param[1].replace('&lang', '')
            b= document.getElementsByTagName('source')
            var track = document.createElement('track')
            label = document.createAttribute('kind')
            label.value="subtitles"
            srclang = document.createAttribute('srclang')
            srclang.value = srclang
            src = document.createAttribute('src')
            src.value = src2
            track.setAttributeNode(label)
            track.setAttributeNode(srclang2)
            track.setAttributeNode(src)
            b.appendChild(track)

        });