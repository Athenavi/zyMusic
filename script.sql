create table artists
(
    ArtistID   int auto_increment
        primary key,
    Name       varchar(255)                       not null,
    Bio        text                               null,
    DebutDate  date                               null,
    Country    varchar(255)                       null,
    CreateTime datetime default CURRENT_TIMESTAMP null,
    UpdateTime datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP
)
    engine = InnoDB;

create table albums
(
    AlbumID        int auto_increment
        primary key,
    Title          varchar(255)                       not null,
    ArtistID       int                                null,
    ReleaseDate    date                               null,
    Genre          varchar(100)                       null,
    CoverImagePath varchar(255)                       null,
    CreateTime     datetime default CURRENT_TIMESTAMP null,
    UpdateTime     datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint albums_ibfk_1
        foreign key (ArtistID) references artists (ArtistID)
)
    engine = InnoDB;

create index ArtistID
    on albums (ArtistID);

create table hot
(
    HotID      int auto_increment
        primary key,
    TargetID   int                                          not null,
    Type       enum ('SONG', 'ARTIST', 'ALBUM', 'PLAYLIST') not null,
    Position   int       default 0                          null,
    UpdateTime timestamp default CURRENT_TIMESTAMP          null on update CURRENT_TIMESTAMP,
    constraint unique_target_type
        unique (TargetID, Type)
)
    engine = InnoDB;

create table musictags
(
    TagID   int auto_increment
        primary key,
    TagName varchar(255) not null,
    constraint TagName
        unique (TagName)
)
    engine = InnoDB;

create table songs
(
    SongID         int auto_increment
        primary key,
    Title          varchar(255)                       not null,
    ArtistID       int                                null,
    AlbumID        int                                null,
    Genre          varchar(100)                       null,
    Duration       int                                null comment 'Duration in seconds',
    ReleaseDate    date                               null,
    FilePath       varchar(255)                       null comment 'Path to where the song file is stored',
    CoverImagePath varchar(255)                       null,
    Lyrics         text                               null,
    Language       varchar(50)                        null,
    PlayCount      int      default 0                 null,
    CreateTime     datetime default CURRENT_TIMESTAMP null,
    UpdateTime     datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint songs_ibfk_1
        foreign key (ArtistID) references artists (ArtistID),
    constraint songs_ibfk_2
        foreign key (AlbumID) references albums (AlbumID)
)
    engine = InnoDB;

create index AlbumID
    on songs (AlbumID);

create index ArtistID
    on songs (ArtistID);

create index idx_title
    on songs (Title);

create table songtags
(
    SongID int not null,
    TagID  int not null,
    primary key (SongID, TagID),
    constraint songtags_ibfk_1
        foreign key (SongID) references songs (SongID)
            on delete cascade,
    constraint songtags_ibfk_2
        foreign key (TagID) references musictags (TagID)
            on delete cascade
)
    engine = InnoDB;

create index TagID
    on songtags (TagID);

create table users
(
    UserID                        int auto_increment
        primary key,
    Username                      varchar(255)                                               not null,
    Password                      varchar(255)                                               not null,
    Email                         varchar(255)                                               not null,
    Mobile                        varchar(20)                                                null,
    CreatedTime                   timestamp                        default CURRENT_TIMESTAMP null,
    UpdatedTime                   timestamp                        default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    LastLoginTime                 timestamp                                                  null,
    Status                        tinyint                          default 1                 null,
    Role                          varchar(50)                                                null,
    Nickname                      varchar(255)                                               null,
    Avatar                        varchar(255)                                               null,
    Gender                        enum ('Male', 'Female', 'Other') default 'Other'           null,
    Birthday                      date                                                       null,
    Country                       varchar(255)                                               null,
    City                          varchar(255)                                               null,
    Bio                           text                                                       null,
    TwoFactorAuthenticationStatus tinyint                          default 0                 null,
    constraint Email
        unique (Email),
    constraint Mobile
        unique (Mobile)
)
    engine = InnoDB;

create table comments
(
    CommentID       int auto_increment
        primary key,
    SongID          int                                null,
    UserID          int                                null,
    ParentCommentID int                                null,
    Content         text                               null,
    ImageURL        varchar(255)                       null,
    LikesCount      int      default 0                 null,
    MentionedUsers  text                               null comment '@功能，存储被提及用户的UserID，逗号分隔',
    CreateTime      datetime default CURRENT_TIMESTAMP null,
    UpdateTime      datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint comments_ibfk_1
        foreign key (SongID) references songs (SongID),
    constraint comments_ibfk_2
        foreign key (UserID) references users (UserID)
)
    engine = InnoDB;

create index SongID
    on comments (SongID);

create index UserID
    on comments (UserID);

create table follows
(
    FollowID   int auto_increment
        primary key,
    UserID     int                                          not null,
    TargetID   int                                          not null,
    Type       enum ('USER', 'ARTIST', 'ALBUM', 'PLAYLIST') not null,
    CreateTime timestamp default CURRENT_TIMESTAMP          null,
    constraint unique_follow
        unique (UserID, TargetID, Type),
    constraint follows_ibfk_1
        foreign key (UserID) references users (UserID)
)
    engine = InnoDB;

create table message
(
    MessageID      int auto_increment
        primary key,
    SenderID       int                                  not null,
    ReceiverID     int                                  not null,
    MessageContent text                                 not null,
    SentTime       datetime   default CURRENT_TIMESTAMP not null,
    IsRead         tinyint(1) default 0                 not null,
    constraint message_ibfk_1
        foreign key (SenderID) references users (UserID)
            on delete cascade,
    constraint message_ibfk_2
        foreign key (ReceiverID) references users (UserID)
            on delete cascade
)
    engine = InnoDB;

create index ReceiverID
    on message (ReceiverID);

create index SenderID
    on message (SenderID);

create table notifications
(
    NotificationID int auto_increment
        primary key,
    UserID         int                                null,
    Type           enum ('MENTION', 'SYSTEM')         not null,
    Content        text                               not null,
    IsRead         tinyint  default 0                 null comment '标记是否已读，0为未读，1为已读',
    ReferenceID    int                                null comment '根据类型，可能关联不同的ID，如COMMENTID',
    CreateTime     datetime default CURRENT_TIMESTAMP null,
    constraint notifications_ibfk_1
        foreign key (UserID) references users (UserID)
)
    engine = InnoDB;

create index UserID
    on notifications (UserID);

create table playlists
(
    PlaylistID  int auto_increment
        primary key,
    UserID      int                                  not null,
    Name        varchar(255)                         not null,
    Description text                                 null,
    Public      tinyint(1) default 1                 null,
    CreateTime  timestamp  default CURRENT_TIMESTAMP null,
    UpdateTime  timestamp  default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint playlists_ibfk_1
        foreign key (UserID) references users (UserID)
)
    engine = InnoDB;

create table playlist_songs
(
    PlaylistSongID int auto_increment
        primary key,
    PlaylistID     int not null,
    SongID         int not null,
    constraint playlist_songs_ibfk_1
        foreign key (PlaylistID) references playlists (PlaylistID)
            on update cascade on delete cascade,
    constraint playlist_songs_ibfk_2
        foreign key (SongID) references songs (SongID)
            on update cascade on delete cascade
)
    engine = InnoDB;

create index PlaylistID
    on playlist_songs (PlaylistID);

create index SongID
    on playlist_songs (SongID);

create index UserID
    on playlists (UserID);

create table useractivitylogs
(
    ID                  int auto_increment
        primary key,
    UserID              int                                not null,
    ActivityType        varchar(100)                       not null,
    ActivityDescription text                               null,
    IPAddress           varchar(45)                        not null,
    Timestamp           datetime default CURRENT_TIMESTAMP not null,
    constraint useractivitylogs_ibfk_1
        foreign key (UserID) references users (UserID)
            on delete cascade
)
    engine = InnoDB;

create index UserID
    on useractivitylogs (UserID);

create index idx_username
    on users (Username);

create table vips
(
    VIPID         int auto_increment
        primary key,
    UserID        int                                not null,
    VIPLevel      int      default 1                 not null,
    VIPPoints     int      default 0                 null,
    StartDate     datetime default CURRENT_TIMESTAMP null,
    EndDate       datetime                           null,
    RenewalStatus tinyint  default 0                 null comment '0 for not renewed, 1 for renewed',
    SpecialNotes  text                               null,
    constraint UserID
        unique (UserID),
    constraint vips_ibfk_1
        foreign key (UserID) references users (UserID)
)
    engine = InnoDB;


