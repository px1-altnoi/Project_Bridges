# Maya側使い方
　AltArcをフォルダーごとダウンロードして”~/documents/maya/2020/scripts”に置きます。
スクリプトエディタに
```python:shelf.py
import AltArc.arcUI
ui = AltArc.arcUI.arcMainUI()
ui.show_dialog()
```
とかけば正しくインストールされていれば、ツールが立ち上がります。
 これをshelfに登録しておきたい場合は`file > save script to shelf`から行うことが可能です。
 書き出したい部分にロケーターおいて適切なものの子にしてやりそのロケーターを選択した状態で対象カメラと出力先を選択して実行してやるだけです。

# AE側使い方
　まず、Mayaでレンダリングしたデータをあらかじめ取り込んでコンポジションを作っておきます。

　その作業が終わったら、File > Scriptでファイル選択する画面が出てきますので先ほどダウンロードしたAltArcフォルダーの中にあるarcAE.jsxを選択し実行します。立ち上がったら先ほど出力したファイルをTarget Fileに、入力したいオブジェクト名を選択し、出力対象のコンポジション名を指定します。あとはActionを実行してやれば取り込まれます。
