// viewportOverlayPlugin.cpp
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MHWRender/MFrameContext.h>
#include <maya/MHWRender/MUIDrawManager.h>
#include <GL/gl.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>

// UserData class to pass widget textures
class ViewportUIData : public MUserData {
public:
    ViewportUIData() : MUserData(false), headerTex(0), sideTex(0) {}
    ~ViewportUIData() {
        if (headerTex) glDeleteTextures(1, &headerTex);
        if (sideTex) glDeleteTextures(1, &sideTex);
    }
    GLuint headerTex;
    GLuint sideTex;
    int headerW, headerH;
    int sideW, sideH;
};

// Base locator node
class ViewportOverlayNode : public MPxLocatorNode {
public:
    static MTypeId id;
    static MString typeName;
    static void* creator() { return new ViewportOverlayNode(); }
    static MStatus initialize() { return MS::kSuccess; }
    MBoundingBox boundingBox() const override {
        return MBoundingBox();
    }
};

MTypeId ViewportOverlayNode::id(0x87014);
MString ViewportOverlayNode::typeName("viewportOverlayNode");

// DrawOverride class
class ViewportOverlayDrawOverride : public MHWRender::MPxDrawOverride {
public:
    static MHWRender::MPxDrawOverride* Creator(const MObject& obj) {
        return new ViewportOverlayDrawOverride(obj);
    }
    ViewportOverlayDrawOverride(const MObject& obj)
        : MPxDrawOverride(obj, nullptr, true) {}

    MHWRender::DrawAPI supportedDrawAPIs() const override {
        return MHWRender::kAllDevices;
    }

    MString drawRegistrantId() const override {
        return "viewportOverlayDraw";
    }

    bool isBounded(const MDagPath& objPath, const MDagPath& cameraPath) const override {
        return false;
    }

    MBoundingBox boundingBox(const MDagPath& objPath, const MDagPath& cameraPath) const override {
        return MBoundingBox();
    }

    MUserData* prepareForDraw(const MDagPath& objPath,
                              const MDagPath& cameraPath,
                              const MHWRender::MFrameContext& frameContext,
                              MUserData* oldData) override {
        ViewportUIData* data = dynamic_cast<ViewportUIData*>(oldData);
        if (!data) data = new ViewportUIData();

        // TODO: render PySide2 widgets to QImage, upload to OpenGL textures
        // For demonstration, generate simple colored textures
        if (!data->headerTex) {
            glGenTextures(1, &data->headerTex);
            glBindTexture(GL_TEXTURE_2D, data->headerTex);
            data->headerW = 200; data->headerH = 30;
            // Upload blank texture or actual widget content here
            std::vector<unsigned char> pix(data->headerW * data->headerH * 4, 255);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, data->headerW, data->headerH, 0, GL_RGBA, GL_UNSIGNED_BYTE, pix.data());
        }
        if (!data->sideTex) {
            glGenTextures(1, &data->sideTex);
            glBindTexture(GL_TEXTURE_2D, data->sideTex);
            data->sideW = 200; data->sideH = 400;
            std::vector<unsigned char> pix(data->sideW * data->sideH * 4, 128);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, data->sideW, data->sideH, 0, GL_RGBA, GL_UNSIGNED_BYTE, pix.data());
        }
        glBindTexture(GL_TEXTURE_2D, 0);
        return data;
    }

    void addUIDrawables(const MDagPath& objPath,
                        MHWRender::MUIDrawManager& drawManager,
                        const MHWRender::MFrameContext& frameContext,
                        const MUserData* data) override {
        const ViewportUIData* uiData = static_cast<const ViewportUIData*>(data);
        int vpWidth = frameContext.getViewportWidth();
        int vpHeight = frameContext.getViewportHeight();

        // Draw header
        drawManager.beginDrawable();
        drawManager.setTexture(uiData->headerTex);
        drawManager.image2d(0, vpHeight - uiData->headerH, uiData->headerW, uiData->headerH);
        drawManager.endDrawable();

        // Draw side panel
        drawManager.beginDrawable();
        drawManager.setTexture(uiData->sideTex);
        drawManager.image2d(vpWidth - uiData->sideW, 0, uiData->sideW, uiData->sideH);
        drawManager.endDrawable();
    }
};

// Plugin registration
MStatus initializePlugin(MObject obj) {
    MFnPlugin plugin(obj, "YourName", "1.0", "Any");
    plugin.registerNode(
        ViewportOverlayNode::typeName,
        ViewportOverlayNode::id,
        ViewportOverlayNode::creator,
        ViewportOverlayNode::initialize,
        MPxNode::kLocatorNode
    );
    MHWRender::MDrawRegistry::registerDrawOverrideCreator(
        ViewportOverlayNode::typeName,
        ViewportOverlayNode::typeName,
        ViewportOverlayDrawOverride::Creator
    );
    MGlobal::executeCommand("createNode " + ViewportOverlayNode::typeName);
    return MS::kSuccess;
}

MStatus uninitializePlugin(MObject obj) {
    MFnPlugin plugin(obj);
    MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(
        ViewportOverlayNode::typeName,
        ViewportOverlayNode::typeName
    );
    plugin.deregisterNode(ViewportOverlayNode::id);
    return MS::kSuccess;
}