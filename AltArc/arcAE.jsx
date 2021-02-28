/*=====================================
AltArc version 1.0.0

Copyrights(c) 2021 altnoi

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
=====================================*/

// function =====================================
function SelectFile(){
    var FileObj = File.openDialog("ターゲットフォルダを選択");
    var FileText = FileObj.toString();
    if(FileText.charAt(0) === "/"){
        FileText = FileText.substr(1, FileText.length - 1);
    }
    return FileText;
}

function GetComps(){
    for(var i = 1;i<=app.project.items.length;i++){
        comps.push(app.project.items[i]);
    }
    return comps;
}

ItemCollection.prototype.getAllComposition = function() {
    var comps = [];
    for(var i = 1;i<this.length;i++){
        var curItem = this[i];
        if(curItem && curItem instanceof CompItem){
            comps.push(curItem);
        }
    }
    return comps;
};

// Main window ==================================
function CreateMainWindow() {
    var XMLData = "";

    var WindowObj = new Window("window", "AltArc AE Internal Beta", [0, 0, 500, 400]);

    var PathGrp = WindowObj.add("panel", [10, 10, 480, 60], "Target File");
    var PathLe = PathGrp.add("edittext", [20, 10, 360, 30], "");
    var PathBtn = PathGrp.add("button", [380, 10, 460, 30], "Select File");

    var ObjGrp = WindowObj.add("panel", [10, 70, 480, 120], "Target Object");
    var ObjList = ObjGrp.add("dropdownlist", [20, 10, 360, 30], []);
    var ObjReloadBtn = ObjGrp.add("button", [380, 10, 460, 30], "Reload");

    var CompGrp = WindowObj.add("panel", [10, 130, 480, 180], "Target Composition");
    var CompList = CompGrp.add("dropdownlist", [20, 10, 360, 30], []);
    var CompReloadBtn = CompGrp.add("button", [380, 10, 460, 30], "Load comp");

    var ActionBtn = WindowObj.add("button", [400, 350, 480, 390], "Action");
    var ErrorInfo = WindowObj.add("statictext", [20, 320, 300, 340], "");
    var BuildInfo = WindowObj.add("statictext", [20, 350, 300, 390], "Build info : 1.0.0");

    // Function
    function SetCompList(){
        CompList.removeAll();
        var comps = app.project.items.getAllComposition();
        for (var i = 0; i < comps.length; i++) {
            CompList.add("item", comps[i].name);
        }
        CompList.selection = 0;
    }

    function SetObjList(path){
        XMLData = "";
        var fObj = new File(path);
        var flg = fObj.open("r");
        if(flg === true) {
            var text = fObj.read();
            XMLData = new XML(text);
            ObjList.removeAll();
            for(var i = 0;i<XMLData.contents.length();i++){
                ObjList.add("item", XMLData.contents[i].name);
            }
            ObjList.selection = 0;
        }else{
            alert("Error!!! Check Error Message Bellow.");
            ErrorInfo.text = "Target Fileで指定されたファイルが開けません";
        }
    }

    function InputDataCheck(){
        /*
        アクションクリック時に各種入力パラメータの正当性検証
         */
        if(XMLData === ""){
            // XMLのデータが前処理として入力されていなければいけないため
            return false;
        }

        if(ObjList.items === ""){
            // 追跡対象オブジェクトが指定されている必要があるため
            return false;
        }

        return true;
    }

    // Action
    PathBtn.onClick = function(){
        path = SelectFile();
        PathLe.text = path;
        SetObjList(path);
    }

    ObjReloadBtn.onClick = function(){
        path = PathLe.text;
        if(path.charAt(0) !== "~" || path.charAt(0) !== "/") {
            path = "/" + path;
        }
        SetObjList(path);
    }

    CompReloadBtn.onClick = function() {
        SetCompList();
    }

    ActionBtn.onClick = function(){
        if(InputDataCheck()) {
            var XMLTargetIndex = ObjList.selection.index;
            // app.project.itemは1-オリジン
            var ImportTargetItemIndex = CompList.selection.index + 1;
            var FrameDuration = app.project.item(ImportTargetItemIndex).frameDuration;

            // add layer
            var WriteOnShapeLayer = app.project.item(ImportTargetItemIndex).layers.addShape();
            // set effect "write on"
            var WriteOnEffect = WriteOnShapeLayer.property("ADBE Effect Parade").addProperty("ADBE Write-on");
            var WriteOnPos = WriteOnEffect.property("ADBE Write-on-0001");

            // set data
            for(var i = 0;i<XMLData.contents[XMLTargetIndex].value.length();i++){
                var pos = [Number(XMLData.contents[XMLTargetIndex].value[i].x), Number(XMLData.contents[XMLTargetIndex].value[i].y)];
                WriteOnPos.setValueAtTime(FrameDuration * i, pos);
            }
        }else{
            alert("Error!!! Check Error Message Bellow.");
            ErrorInfo.text = "入力データが不正です。Target fileとTarget objectが正しく指定されているかご確認ください";
        }
        alert("Done.");
    }

    // Refresh UI
    SetCompList();

    return WindowObj;
}

// Main function ================================
var MainWindow = CreateMainWindow();
MainWindow.center();
MainWindow.show();
