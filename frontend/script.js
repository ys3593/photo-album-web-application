var apigClient = apigClientFactory.newClient({apiKey: "oCRcvmU1Z84ahAO8vScTD1ZZ6IqKX3GQ1h3SRtxn"});
var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
var recognition = new SpeechRecognition()


function search() {
    var inputtext = document.getElementById("searchkeywords").value;
    console.log("Searching for " + inputtext);

    var params = {
        "q": inputtext,
    };

    var body = {};
    var additionalParams = {};
    apigClient.searchGet(params, body, additionalParams)
        .then(function (result) {
            console.log("search result success");
            console.log(result);
            console.log(result.data);
            display(result.data);
        }).catch(function (result) {
            console.log("search result fail");
        });
}

function display(result) {
    var displayimg = document.getElementById("imgs");
    console.log(displayimg);

    while (displayimg.firstChild) {
        displayimg.removeChild(displayimg.firstChild)
    }

    var ra = result;
    console.log(ra);

    for (var i = 0; i < ra.length; i++) {
        console.log(ra[i])
        var displayimg = document.getElementById("imgs");
        var img = document.createElement("img");
        img.classList.add();
        img.src = ra[i];
        img.style.height = '300px';
        displayimg.appendChild(img);
    }
}



function upload() {
    var fileReader = new FileReader();
    var fileLocation = (document.getElementById("fileinput").value).split("\\");
    var fileName = fileLocation.at(-1);
    var fileObject = document.getElementById("fileinput").files[0];

    const file = document.getElementById("fileinput").files[0];

    file.constructor = () => file;

    var imgtypeArr = ["jpeg", "png", "jpg"];
    if ((!fileLocation) || (!imgtypeArr.some(type => fileName.includes(type)))) {
        alert("Not Valid")
    }
    else {
        console.log("upload image");
        var customLabel = document.getElementById("customlabel").value;

        var params = {
            item: fileName,
            folder: "cs6998storephotos",
            "Content-Type": "image/jpeg",
            "x-amz-meta-customLabels": customLabel,
            'Access-Control-Allow-Headers':'*',
            headers: {
                "Content-Type": "image/jpeg",
                "Access-Control-Allow-Origin" : "*",
                "x-amz-meta-customLabels": customLabel,
            }
        };

        var additionalParams = {
            headers: {
                "Content-Type": "image/jpeg",
                "Access-Control-Allow-Origin" : "*",
                "x-amz-meta-customLabels": customLabel,
            }
        };

        fileReader.onload = function (event) {
            eventBody = event.target.result;

            body = btoa(eventBody)
            return apigClient.uploadFolderItemPut(params, file, additionalParams)
                .then(function (result) {
                    console.log(result);
                })
                .catch(function (error) {
                    console.log(error);
                })
        }
        fileReader.readAsBinaryString(fileObject)
    }
}


function searchVoice() {
    recognition.start();
    recognition.onresult = (event) => {
        var text = event.results[0][0].transcript;
        console.log(text)
        document.getElementById("searchkeywords").value = text
        search();
    }
}