

手順まとめるよ

1.	A-cell側で生成した Sim_prog.cpp, Sim_cond.cnd をもってくる

2.	A-cellのパスウェイ編集画面にてクロスレファレンスを表示、コピペするとhtmlとして得られるので、これを s-g.html としてもってくる

3.	sh-createJSON.shを実効。
	これにより
		concentration.json    :	分子や速度定数の初期値をまとめた配列
		symbol-group.json     :	どのシンボルがどの反応系に含まれるかを示したもの
		editthisgrouplist.txt :	どの反応系がどのタイプのコンパートメントの種類に含まれるかを示したもの
	が生成される。

4.	editthisgrouplist.txt は名前のとおり、JSONとしては未完成だ。
	各種反応系がどのタイプのコンパートメントに属するかを埋めて、 group-compartment.json として保存しよう。
	"cytosolic diffusion" のように複数種の反応系に含まれる反応系は、次のように正規化して複数行に記述する。

		["Cytosolic&nbsp;Diffusion", "A"],
		["Cytosolic&nbsp;Diffusion", "B"],
		["Cytosolic&nbsp;Diffusion", "."],

	末尾のコンマは消し忘れがちなので注意。
	コンパートメントの区分としてここに記述した名称は、あとでそのままモデルの設計に使用される。
	アルファベット大文字1文字あるいは記号（'.', ',', '%', '&', '#', '@' など）が無難。
	複数文字の羅列や、ひらがなカタカナ漢字は多分バグるのでやめましょう。

5.	generator.py, model.py をもってくる

6.	いじる。
	model.py にはいくつか文字列がハードコードされている。

		・参照するJSONファイル名（ここはいじらなくていい）
		・	"reactionFlags()"下 - どのコンパートメントが、どの反応系を持つべきかを示す 01 の羅列。
			コンパートメント区分にはステップ4の区分を流用しよう。
			01の羅列は、A-cell側で各タイプのコンパートメントに反応系を割り振った上でプログラムを生成すればそれぞれに対応した羅列が Sim_cond.cnd に自ずと記載されるので、これをコピペすると楽。
		・	"exists()"下 - コンパートメントが存在しないことを示す文字。
		・参照する我流4Dデータのファイル名（今は"bluebrint.txt"とかそんなん）

7.	4Dデータを用意（Vsim ファイルじゃないぞ）
	サンプルを見た方が早いと思う。
	一文字一コンパートメントで、対応関係は group-compartment.json & model.py に記述してきた通り。
	一行目は
		x方向のサイズ	y方向のサイズ	z方向のサイズ
	と書く。これに依存して色々決定されるので更新を忘れずに。

8.	まずはエラーがでないか、それとコンパートメント数はどんなもんか確認
		$ python3 compartmentN.py
	良さげであればこっちを実行
		$ python3 generator.py > dump
	改行がwindows環境のそれ（0x0D0A）じゃないとバグるっぽいので、linux等では
		$ python3 generator.py | nkf --windows > dump

9.	手順8で得たコンパートメント数を Sim_prog.cpp, Sim_cond.cnd の該当個所に適用（それぞれ一ヶ所）。
		$ ./sh-updateN.sh xxxxx

10.	手順8で得た dump を Sim_cond.cnd に適用。もとの設定は上書き・消去されることになる。
		$ ./sh-merge.sh

11.	以上で Sim_prog.cpp, Sim_cond.cnd が更新されたはずなので好きなワークステーションでコンパイル・実行。

--2017.12.19
