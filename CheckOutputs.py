import sys
import os

def FileExists(folderpath, errorFile, ScanID, FileSuffix):
	inputFile = os.path.join(folderpath, str(ScanID) + FileSuffix)
	if os.path.isfile(inputFile):
		errorFile.write(", Yes ")
		return
	errorFile.write(", No ")


def main():
	
	if len(sys.argv) < 4:
		print "correct usage: python CheckOutputs.Py <startIndex> <EndIndex> <DatabaseDirectory>"
		return
	try:
		start = int(sys.argv[1])
		end = int(sys.argv[2])
	except Exception, e:
		raise e

	output = open("ScanDataAtLandmarks.csv", 'w')
	output.write("ScanID, TVC Cross-sectional Area, TVC Perimeter, TVC COM , Subglottic Cross-sectional Area, Subglottic Perimeter, Subglottic COM , InferriorSubglottis Cross-sectional Area, InferriorSubglottis Perimeter, InferriorSubglottis COM, MinSliceID, MinSlice Cross-sectional Area, MinSlice Perimeter, MinSlice COM, MidTrachea Cross-sectional Area, MidTrachea Perimeter, MidTrachea COM\n")
	errors = open("Errors.csv", 'w')
	errors.write("ScanID, has _OUTPUT.nrrd, has _LANDMARKS.txt, has _CLIPPINGS.txt, has _OUTPUT.vtp, _HEATFLOW.mha, _MOUTH_REMOVED.nrrd, _MOUTH_REMOVED.vtp, _ALL_CROSS_SECTIONS.vtp \n")

	for ScanID in xrange(start, end+1):


		f = os.path.join(sys.argv[3], str(ScanID), str(ScanID) + "_CROSS_SECTIONS_AT_LANDMARKS.csv")
		if os.path.isfile(f):
			o = open(f, 'r')
			for line in o:
				output.write(line)
			continue

		folder = os.path.join(sys.argv[3], str(ScanID))
		errors.write("%d " % (ScanID))
		FileExists(folder, errors, ScanID, "_OUTPUT.nrrd")
		FileExists(folder, errors, ScanID, "_LANDMARKS.txt")
		FileExists(folder, errors, ScanID, "_CLIPPINGS.txt")
		FileExists(folder, errors, ScanID, "_OUTPUT.vtp")
		FileExists(folder, errors, ScanID, "_HEATFLOW.mha")
		FileExists(folder, errors, ScanID, "_MOUTH_REMOVED.nrrd")
		FileExists(folder, errors, ScanID, "_MOUTH_REMOVED.vtp")
		FileExists(folder, errors, ScanID, "_ALL_CROSS_SECTIONS.vtp")
		errors.write("\n")

	# print total, count
##---------------------------------------------------
if __name__ == '__main__':
	main()