import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sembast/sembast_io.dart';
import 'package:sembast_web/sembast_web.dart';

import '../models/scan_record.dart';

class ScanHistoryDb {
  ScanHistoryDb._();

  static final ScanHistoryDb instance = ScanHistoryDb._();

  static const _dbName = 'scan_history.db';
  static const _storeName = 'scans';

  final StoreRef<int, Map<String, dynamic>> _store = intMapStoreFactory.store(_storeName);
  Database? _db;

  DatabaseFactory get _databaseFactory => kIsWeb ? databaseFactoryWeb : databaseFactoryIo;

  // Opens the database, creating it if it doesn't exist
  Future<Database> _openDb() async {
    if (_db != null) {
      return _db!;
    }

    if (kIsWeb) {
      return _databaseFactory.openDatabase(_dbName);
    }

    final dir = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dir.path, _dbName);
    _db = await _databaseFactory.openDatabase(dbPath);
    return _db!;
  }

  // Helper method to perform a database action with automatic opening and optional closing
  Future<T> _withDb<T>(Future<T> Function(Database db) action) async {
    final db = await _openDb();
    try {
      return await action(db);
    } finally {
      if (kIsWeb) {
        await db.close();
      }
    }
  }

  // Inserts a new scan record into the database and returns its generated ID
  Future<int> insertScan(ScanRecord record) async {
    return _withDb((db) => _store.add(db, record.toMap()));
  }

  // Updates an existing scan record by its ID
  Future<void> updateScan(int id, ScanRecord record) async {
    await _withDb((db) => _store.record(id).put(db, record.toMap()));
  }

  // Retrieves all scan records from the database, sorted by timestamp descending
  Future<List<ScanRecord>> getAllScans() async {
    return _withDb((db) async {
      final snapshots = await _store.find(
        db,
        finder: Finder(sortOrders: [SortOrder('timestamp', false)]),
      );

      return snapshots
          .map((snapshot) => ScanRecord.fromMap(snapshot.key, snapshot.value))
          .toList();
    });
  }

  // Deletes a scan record by its ID
  Future<void> deleteScan(int id) async {
    await _withDb((db) => _store.record(id).delete(db));
  }

  // Clears all scan records from the database
  Future<void> clearScans() async {
    await _withDb((db) => _store.delete(db));
  }
}
