import math
from flask import Flask, render_template, request, flash
from random import shuffle
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super secret'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        lokasi = request.form['lokasi']
        tahun_kendaraan = request.form['tahun_kendaraan']
        jumlah_kursi = request.form['jumlah_kursi']
        pendapatan = request.form['pendapatan']
        jumlah_kendaraan = request.form['jumlah_kendaraan']
        k = request.form['k']

		
        if not tahun_kendaraan:
            flash('Masukkan Datanya Dulu Bro?', 'warning')
            return render_template('base.html')
        if not jumlah_kursi:
            flash('Masukkan Datanya Dulu Bro ?', 'warning')
            return render_template('base.html')
        if not pendapatan:
            flash('Masukkan Datanya Dulu Bro ?', 'warning')
            return render_template('base.html')
        if not jumlah_kendaraan:
            flash('Masukkan Datanya Dulu Bro ?', 'warning')
            return render_template('base.html')
        if not lokasi:
            flash('Masukkan Datanya Dulu Bro?', 'warning')
            return render_template('base.html')
        if not k:
            flash('Masukkan Datanya Dulu Bro', 'warning')
            return render_template('base.html')

        items = pd.read_csv('dataset.txt')

        # Konversi nilai input ke tipe yang sesuai
        lokasi = (lokasi)
        tahun_kendaraan = int(tahun_kendaraan)
        jumlah_kursi = int(jumlah_kursi)
        pendapatan = int(pendapatan)
        jumlah_kendaraan = int(jumlah_kendaraan)
        k = int(k)

        # Buat item baru sebagai dictionary
        newItem = {
            'TahunKendaraan': tahun_kendaraan,
            'JumlahKursi': jumlah_kursi,
            'Pendapatan': pendapatan,
            'JumlahKendaraan': jumlah_kendaraan
        }

        # Konversi baris DataFrame ke dictionary
        items_dict = items.to_dict(orient='records')

        # Klasifikasikan item baru
        accuracy2, maxi, count, neighbors = Classify(newItem, k, items_dict)

        # Siapkan data untuk ditampilkan
        skor = pd.DataFrame(neighbors, columns=['Skor', 'Hasil Keputusan'])
        keputusan = pd.DataFrame(list(count.items()), columns=['Hasil Keputusan', 'Jumlah'])

        return render_template(
            'base.html',
            keputusan=keputusan.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'),
            skor=skor.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'),
			lokasi=lokasi,
            tahun_kendaraan=tahun_kendaraan,
            jumlah_kursi=jumlah_kursi,
            pendapatan=pendapatan,
            jumlah_kendaraan=jumlah_kendaraan,
            evaluat=accuracy2,
            items=items,
            k=k
        )

    return render_template('base.html')


@app.route('/dataset')
def dataset():
    try:
        # Read the CSV file into a DataFrame
        items = pd.read_csv('dataset.txt')
        
        # Ensure columns with numeric data are properly converted to appropriate types
        numeric_columns = ['TahunKendaraan', 'JumlahKursi', 'Pendapatan', 'JumlahKendaraan']
        for column in numeric_columns:
            items[column] = pd.to_numeric(items[column], errors='coerce')
        
        # Optionally, handle missing or NaN values if necessary
        items.fillna(0, inplace=True)  # Fill NaNs with 0
        
        # Render the DataFrame to HTML with the specified classes
        return render_template('dataset.html', items=items.to_html(classes='table table-striped table-hover table-bordered table-sm table-responsive-sm'))
    
    except ValueError as e:
        return f"ValueError: {e}"
    except Exception as e:
        return f"An error occurred: {e}"


def EuclideanDistance(x, y):
    S = 0
    for key in x.keys():
        S += math.pow(x[key] - y[key], 2)
    return math.sqrt(S)


def CalculateNeighborsClass(neighbors, k):
    count = {}
    for i in range(k):
        if neighbors[i][1] not in count:
            count[neighbors[i][1]] = 1
        else:
            count[neighbors[i][1]] += 1
    return count


def FindMax(Dict):
    maximum = -1
    classification = ''

    for key in Dict.keys():
        if Dict[key] > maximum:
            maximum = Dict[key]
            classification = key
    return classification, maximum


def UpdateNeighbors(neighbors, item, distance, k):
    neighbors.append([distance, item['HasilKeputusan']])
    neighbors.sort(key=lambda x: x[0])
    return neighbors[:k]


def Classify(nItem, k, Items):
    if k > len(Items):
        return "k lebih besar dari jumlah item"

    neighbors = []
    for item in Items:
        distance = EuclideanDistance(nItem, item)
        neighbors = UpdateNeighbors(neighbors, item, distance, k)

    count = CalculateNeighborsClass(neighbors, k)
    klas, maxi = FindMax(count)

    return klas, maxi, count, neighbors


if __name__ == '__main__':
    app.run(debug=True, port=5000)
