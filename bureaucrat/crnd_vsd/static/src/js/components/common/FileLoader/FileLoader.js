/** @odoo-module **/
import { Component, useState, useRef, onWillUpdateProps } from "@odoo/owl";


export class FileLoader extends Component {
  static template = "crnd_vsd.FileLoader";

  fileInputRef = useRef("file_input");

  mergeFileLists(fileList1, fileList2) {
    const mergedFiles = [];
  
    // Преобразуем FileList в массивы
    const filesArray1 = Array.from(fileList1);
    const filesArray2 = Array.from(fileList2);
  
    // Объединяем два массива
    const allFiles = [...filesArray1, ...filesArray2];
  
    // Добавляем файлы в итоговый массив, проверяя дубликаты по имени файла и размеру
    allFiles.forEach(file => {
      const isDuplicate = mergedFiles.some(existingFile =>
        existingFile.name === file.name && existingFile.size === file.size
      );
      
      if (!isDuplicate) {
        mergedFiles.push(file);
      }
    });
  
    // Преобразуем обратно в FileList
    return mergedFiles;
  }


  fileInputLoad(event) {
    const selectedFiles = Array.from(event.target.files);
    const allFiles = this.mergeFileLists(this.props.files, selectedFiles)
    this.props.updateFilesList(allFiles)
  }
}
